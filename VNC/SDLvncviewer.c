
#include <SDL2/SDL.h>
#include <signal.h>
#include <rfb/rfbclient.h>
#include <rfb/rfbproto.h>
#include <time.h>
#include <unistd.h>
#include <pthread.h> 

// #include <FL/Fl.H>
// #include <FL/Fl_Image_Surface.H>
// #include <FL/Fl_Scrollbar.H>
// #include <FL/fl_draw.H>
// #include <FL/x.H>

#include "helper.h"

struct
{
	int sdl;
	int rfb;
} buttonMapping[] = {
	{1, rfbButton1Mask},
	{2, rfbButton2Mask},
	{3, rfbButton3Mask},
	{4, rfbButton4Mask},
	{5, rfbButton5Mask},
	{0, 0}};

struct
{
	char mask;
	int bits_stored;
} utf8Mapping[] = {
	{0b00111111, 6},
	{0b01111111, 7},
	{0b00011111, 5},
	{0b00001111, 4},
	{0b00000111, 3},
	{0, 0}};

static int enableResizable = 0, viewOnly, listenLoop, buttonMask;
int sdlFlags;
SDL_Texture *sdlTexture;
SDL_Renderer *sdlRenderer;
SDL_Window *sdlWindow;
SDL_Surface *sdl;
/* client's pointer position */
int x, y;

static int rightAltKeyDown, leftAltKeyDown;

time_t before;
SDL_Rect ping_r = {0,0,0,0};

pthread_mutex_t render_lock;

// Init functions !TODO move to header file
static void initAppData(AppData* data);
static void setEncodings(rfbClient *cl);

static rfbBool resize(rfbClient *client)
{
	pthread_mutex_lock(&render_lock);
	int width = client->width, height = client->height,
		depth = client->format.bitsPerPixel;

	// if (enableResizable)
		sdlFlags |= SDL_WINDOW_RESIZABLE;
	// else
		// sdlFlags |= SDL_WINDOW_FULLSCREEN;

	client->updateRect.x = client->updateRect.y = 0;
	client->updateRect.w = width;
	client->updateRect.h = height;

	/* create or resize the window */
	if (!sdlWindow)
	{
		sdlWindow = SDL_CreateWindow(client->desktopName,
									 SDL_WINDOWPOS_UNDEFINED,
									 SDL_WINDOWPOS_UNDEFINED,
									 width,
									 height,
									 sdlFlags);
		if (!sdlWindow)	
			rfbClientErr("resize: error creating window: %s\n", SDL_GetError());
		
		// sdl = SDL_GetWindowSurface(sdlWindow);
	}
	else
	{
		SDL_SetWindowSize(sdlWindow, width, height);
		// sdl = SDL_GetWindowSurface(sdlWindow);
	}

	/* (re)create the surface used as the client's framebuffer */
	SDL_FreeSurface(rfbClientGetClientData(client, SDL_Init));
	// SDL_Surface *sdl = SDL_CreateRGBSurface(0,
	// 										width,
	// 										height,
	// 										depth,
	// 										0, 0, 0, 0);

	SDL_Surface *sdl = SDL_CreateRGBSurface(0, width, height, depth, 0, 0, 0, 0);
	printf("colorformat: %s", SDL_GetPixelFormatName(sdl->format->format));

	if (!sdl)
		rfbClientErr("resize: error creating surface: %s\n", SDL_GetError());

	rfbClientSetClientData(client, SDL_Init, sdl);
	initAppData(&client->appData);
	client->width = sdl->pitch / (depth / 8);
	client->frameBuffer = sdl->pixels;

	client->format.bitsPerPixel = depth;
	client->format.redShift = sdl->format->Rshift;
	client->format.greenShift = sdl->format->Gshift;
	client->format.blueShift = sdl->format->Bshift;
	client->format.redMax = sdl->format->Rmask >> client->format.redShift;
	client->format.greenMax = sdl->format->Gmask >> client->format.greenShift;
	client->format.blueMax = sdl->format->Bmask >> client->format.blueShift;
	setEncodings(client);
	SetFormatAndEncodings(client);

	// printf("tight=%d, zlib=%d, copyrect=%d, raw=%d, hextile=%d\n", 
	// 	SupportsClient2Server(client, rfbEncodingTight),
	// 	SupportsClient2Server(client, rfbEncodingZlib),
	// 	SupportsClient2Server(client, rfbEncodingCopyRect),
	// 	SupportsClient2Server(client, rfbEncodingRaw),
	// 	SupportsClient2Server(client, rfbEncodingHextile)
	// 	);

	// printf("tight=%d, zlib=%d, copyrect=%d, raw=%d, hextile=%d\n", 
	// 	SupportsServer2Client(client, rfbEncodingTight),
	// 	SupportsServer2Client(client, rfbEncodingZlib),
	// 	SupportsServer2Client(client, rfbEncodingCopyRect),
	// 	SupportsServer2Client(client, rfbEncodingRaw),
	// 	SupportsServer2Client(client, rfbEncodingHextile)
	// 	);

	/* create the renderer if it does not already exist */
	if (!sdlRenderer)
	{
		sdlRenderer = SDL_CreateRenderer(sdlWindow, -1, SDL_RENDERER_ACCELERATED);
		if (!sdlRenderer)
			rfbClientErr("resize: error creating renderer: %s\n", SDL_GetError());
		SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "linear"); /* make the scaled rendering look smoother. */
	}
	SDL_RenderSetLogicalSize(sdlRenderer, width, height); /* this is a departure from the SDL1.2-based version, but more in the sense of a VNC viewer in keeeping aspect ratio */

	/* (re)create the texture that sits in between the surface->pixels and the renderer */
	if (sdlTexture)
		SDL_DestroyTexture(sdlTexture);
	sdlTexture = SDL_CreateTexture(sdlRenderer,
								   sdl->format->format,
								   SDL_TEXTUREACCESS_STREAMING,
								   width, height);
	if (!sdlTexture)
		rfbClientErr("resize: error creating texture: %s\n", SDL_GetError());
	
	pthread_mutex_unlock(&render_lock);
	return TRUE;
}

/* UTF-8 decoding is from https://rosettacode.org/wiki/UTF-8_encode_and_decode which is under GFDL 1.2 */
static rfbKeySym utf8char2rfbKeySym(const char chr[4])
{
	int bytes = strlen(chr);
	int shift = utf8Mapping[0].bits_stored * (bytes - 1);
	rfbKeySym codep = (*chr++ & utf8Mapping[bytes].mask) << shift;
	int i;
	for (i = 1; i < bytes; ++i, ++chr)
	{
		shift -= utf8Mapping[0].bits_stored;
		codep |= ((char)*chr & utf8Mapping[0].mask) << shift;
	}
	return codep;
}

static void update(rfbClient *cl, int x, int y, int w, int h)
{
//	printf("update %d\n", cl->format.bitsPerPixel);
	SDL_Surface *sdl = rfbClientGetClientData(cl, SDL_Init);
	/* update texture from surface->pixels */
	SDL_Rect r = {x, y, w, h};

	if(SDL_RectEquals(&r, &ping_r)) {
		clock_t difference = clock() - before;
		int mssec = difference * 1000 / CLOCKS_PER_SEC;
		printf("Latency between click and response: %d \n", mssec%1000);
	}

	pthread_mutex_lock(&render_lock);
	clock_t render = clock();
	if (SDL_UpdateTexture(sdlTexture, &r, sdl->pixels + y * sdl->pitch + x * (cl->format.bitsPerPixel/8), sdl->pitch) < 0)
		rfbClientErr("update: failed to update texture: %s\n", SDL_GetError());
	clock_t difference = clock() - render;
	int mssec = difference * 1000000 / CLOCKS_PER_SEC;
	printf("tiem to update texture=%d\n", mssec);
	pthread_mutex_unlock(&render_lock);


	// int pitch = sdl->pitch;
	// if(SDL_LockTexture(sdlTexture, &r, sdl->pixels + y * sdl->pitch + x * 4, &pitch) < 0)
		// rfbClientErr("update: failed to update texture: %s\n", SDL_GetError());

	// SDL_UnlockTexture(sdlTexture);

	/* This is fast for surfaces that don't require locking. */
    // /* Once locked, surface->pixels is safe to access. */
    // SDL_LockSurface(sdl);

    // /* This assumes that color value zero is black. Use
    //    SDL_MapRGBA() for more robust surface color mapping! */
    // /* height times pitch is the size of the surface's whole buffer. */
    // SDL_memset(sdl->pixels, 0, sdl->h * sdl->pitch);

    // SDL_UnlockSurface(sdl);

	
	// /* copy texture to renderer and show */
	// if (SDL_RenderClear(sdlRenderer) < 0)
	// 	rfbClientErr("update: failed to clear renderer: %s\n", SDL_GetError());
	// if (SDL_RenderCopy(sdlRenderer, sdlTexture, NULL, NULL) < 0)
	// 	rfbClientErr("update: failed to copy texture to renderer: %s\n", SDL_GetError());
	// SDL_RenderPresent(sdlRenderer);
}

static void *render_screen(void *vargp) {
	sleep(1);
	rfbClient *cl = (rfbClient*)vargp;
	SDL_Surface *sdl = rfbClientGetClientData(cl, SDL_Init);
	int count = 0;
	while(1) 
	{
		count++;
		// Sleep 30ms = 30000us for ~30fps
		// usleep(15000);
		// SendFramebufferUpdateRequest(cl, 0, 0,
			// 							 cl->width, cl->height, TRUE);
		usleep(15000);
		if(sdlRenderer == NULL || sdlTexture == NULL) {
			continue;
		}

		pthread_mutex_lock(&render_lock);
		/* copy texture to renderer and show */
		clock_t before = clock();
		// if (SDL_UpdateTexture(sdlTexture, NULL, sdl->pixels, sdl->pitch) < 0)
			// rfbClientErr("update: failed to update texture: %s\n", SDL_GetError());
		// if (SDL_RenderClear(sdlRenderer) < 0)
			// rfbClientErr("update: failed to clear renderer: %s\n", SDL_GetError());
		if (SDL_RenderCopy(sdlRenderer, sdlTexture, NULL, NULL) < 0)
			rfbClientErr("update: failed to copy texture to renderer: %s\n", SDL_GetError());
		SDL_RenderPresent(sdlRenderer);
		clock_t difference = clock() - before;
		// SDL_UpdateWindowSurface(sdlWindow);
		int mssec = difference * 1000 / CLOCKS_PER_SEC;
		printf("tiem to render=%d\n", mssec);
		if (count == 5)
		{
			SendFramebufferUpdateRequest(cl, 0, 0,
										 cl->width, cl->height, TRUE);
			count = 0;									
		}
		pthread_mutex_unlock(&render_lock);
	}
}

static void drawbitmap(rfbClient* client, const uint8_t* buffer, int x, int y, int w, int h) {
    int j;

  if (client->frameBuffer == NULL) {
      return;
  }

//   if (!CheckRect(client, x, y, w, h)) {
//     rfbClientLog("Rect out of bounds: %dx%d at (%d, %d)\n", x, y, w, h);
//     return;
//   }

#define COPY_RECT(BPP) \
  { \
    int rs = w * BPP / 8, rs2 = client->width * BPP / 8; \
    for (j = ((x * (BPP / 8)) + (y * rs2)); j < (y + h) * rs2; j += rs2) { \
      memcpy(client->frameBuffer + j, buffer, rs); \
      buffer += rs; \
    } \
  }

  switch(client->format.bitsPerPixel) {
  case  8: COPY_RECT(8);  break;
  case 16: COPY_RECT(16); break;
  case 32: COPY_RECT(32); break;
  default:
    rfbClientLog("Unsupported bitsPerPixel: %d\n",client->format.bitsPerPixel);
  }

  update(client, x, y, w, h);
}

static void update_copyrect(rfbClient *cl, int src_x, int src_y, int w, int h, int dest_x, int dest_y)
{
	printf("update_copyrect\n");

	#define COPY_RECT_FROM_RECT(BPP) \
	{ \
		uint##BPP##_t* _buffer=((uint##BPP##_t*)cl->frameBuffer)+(src_y-dest_y)*cl->width+src_x-dest_x; \
		if (dest_y < src_y) { \
			for(int j = dest_y*cl->width; j < (dest_y+h)*cl->width; j += cl->width) { \
				if (dest_x < src_x) { \
					for(int i = dest_x; i < dest_x+w; i++) { \
						((uint##BPP##_t*)cl->frameBuffer)[j+i]=_buffer[j+i]; \
					} \
				} else { \
					for(int i = dest_x+w-1; i >= dest_x; i--) { \
						((uint##BPP##_t*)cl->frameBuffer)[j+i]=_buffer[j+i]; \
					} \
				} \
			} \
		} else { \
			for(int j = (dest_y+h-1)*cl->width; j >= dest_y*cl->width; j-=cl->width) { \
				if (dest_x < src_x) { \
					for(int i = dest_x; i < dest_x+w; i++) { \
						((uint##BPP##_t*)cl->frameBuffer)[j+i]=_buffer[j+i]; \
					} \
				} else { \
					for(int i = dest_x+w-1; i >= dest_x; i--) { \
						((uint##BPP##_t*)cl->frameBuffer)[j+i]=_buffer[j+i]; \
					} \
				} \
			} \
		} \
	}

	SDL_Surface *sdl = rfbClientGetClientData(cl, SDL_Init);
	/* update texture from surface->pixels */
	SDL_Rect src_r = {src_x, src_y, w, h};
	SDL_Rect dest_r = {dest_x, dest_y, w, h};

	switch(cl->format.bitsPerPixel) {
		case  8: COPY_RECT_FROM_RECT(8);  break;
		case 16: COPY_RECT_FROM_RECT(16); break;
		case 32: COPY_RECT_FROM_RECT(32); break;
		default:
			rfbClientLog("Unsupported bitsPerPixel: %d\n",cl->format.bitsPerPixel);
	}

	// pthread_mutex_lock(&render_lock);
	// if (SDL_UpdateTexture(sdlTexture, &dest_r, sdl->pixels + dest_y * sdl->pitch + dest_x * 4, sdl->pitch) < 0)
	// 	rfbClientErr("update: failed to update texture: %s\n", SDL_GetError());
	// pthread_mutex_unlock(&render_lock);
	// /* copy texture to renderer and show */
	// if (SDL_RenderClear(sdlRenderer) < 0)
	// 	rfbClientErr("update: failed to clear renderer: %s\n", SDL_GetError());
	// if (SDL_RenderCopy(sdlRenderer, sdlTexture, NULL, NULL) < 0)
	// 	rfbClientErr("update: failed to copy texture to renderer: %s\n", SDL_GetError());
	// SDL_RenderPresent(sdlRenderer);
}


static rfbBool HandleZlibBPP (rfbClient *client, int rx, int ry, int rw, int rh)
{
  rfbZlibHeader hdr;
  int remaining;
  int inflateResult;
  int toRead;
	printf("zlib");
  /* First make sure we have a large enough raw buffer to hold the
   * decompressed data.  In practice, with a fixed BPP, fixed frame
   * buffer size and the first update containing the entire frame
   * buffer, this buffer allocation should only happen once, on the
   * first update.
   */
  if ( client->raw_buffer_size < (( rw * rh ) * ( client->format.bitsPerPixel / 8 ))) {

    if ( client->raw_buffer != NULL ) {

      free( client->raw_buffer );

    }

    client->raw_buffer_size = (( rw * rh ) * ( client->format.bitsPerPixel / 8 ));
    client->raw_buffer = (char*) malloc( client->raw_buffer_size );

  }

  if (!ReadFromRFBServer(client, (char *)&hdr, sz_rfbZlibHeader))
    return FALSE;

  remaining = rfbClientSwap32IfLE(hdr.nBytes);

  /* Need to initialize the decompressor state. */
  client->decompStream.next_in   = ( Bytef * )client->buffer;
  client->decompStream.avail_in  = 0;
  client->decompStream.next_out  = ( Bytef * )client->raw_buffer;
  client->decompStream.avail_out = client->raw_buffer_size;
  client->decompStream.data_type = Z_BINARY;

  /* Initialize the decompression stream structures on the first invocation. */
  if ( client->decompStreamInited == FALSE ) {

    inflateResult = inflateInit( &client->decompStream );

    if ( inflateResult != Z_OK ) {
      rfbClientLog(
              "inflateInit returned error: %d, msg: %s\n",
              inflateResult,
              client->decompStream.msg);
      return FALSE;
    }

    client->decompStreamInited = TRUE;

  }

  inflateResult = Z_OK;

  /* Process buffer full of data until no more to process, or
   * some type of inflater error, or Z_STREAM_END.
   */
  while (( remaining > 0 ) &&
         ( inflateResult == Z_OK )) {
  
    if ( remaining > RFB_BUFFER_SIZE ) {
      toRead = RFB_BUFFER_SIZE;
    }
    else {
      toRead = remaining;
    }

    /* Fill the buffer, obtaining data from the server. */
    if (!ReadFromRFBServer(client, client->buffer,toRead))
      return FALSE;

    client->decompStream.next_in  = ( Bytef * )client->buffer;
    client->decompStream.avail_in = toRead;

    /* Need to uncompress buffer full. */
    inflateResult = inflate( &client->decompStream, Z_SYNC_FLUSH );

    /* We never supply a dictionary for compression. */
    if ( inflateResult == Z_NEED_DICT ) {
      rfbClientLog("zlib inflate needs a dictionary!\n");
      return FALSE;
    }
    if ( inflateResult < 0 ) {
      rfbClientLog(
              "zlib inflate returned error: %d, msg: %s\n",
              inflateResult,
              client->decompStream.msg);
      return FALSE;
    }

    /* Result buffer allocated to be at least large enough.  We should
     * never run out of space!
     */
    if (( client->decompStream.avail_in > 0 ) &&
        ( client->decompStream.avail_out <= 0 )) {
      rfbClientLog("zlib inflate ran out of space!\n");
      return FALSE;
    }

    remaining -= toRead;

  } /* while ( remaining > 0 ) */

  if ( inflateResult == Z_OK ) {

    /* Put the uncompressed contents of the update on the screen. */
    drawbitmap(client, (uint8_t *)client->raw_buffer, rx, ry, rw, rh);
  }
  else {

    rfbClientLog(
            "zlib inflate returned error: %d, msg: %s\n",
            inflateResult,
            client->decompStream.msg);
    return FALSE;

  }

  return TRUE;
}

static void kbd_leds(rfbClient *cl, int value, int pad)
{
	/* note: pad is for future expansion 0=unused */
	fprintf(stderr, "Led State= 0x%02X\n", value);
	fflush(stderr);
}

/* trivial support for textchat */
static void text_chat(rfbClient *cl, int value, char *text)
{
	switch (value)
	{
	case rfbTextChatOpen:
		fprintf(stderr, "TextChat: We should open a textchat window!\n");
		TextChatOpen(cl);
		break;
	case rfbTextChatClose:
		fprintf(stderr, "TextChat: We should close our window!\n");
		break;
	case rfbTextChatFinished:
		fprintf(stderr, "TextChat: We should close our window!\n");
		break;
	default:
		fprintf(stderr, "TextChat: Received \"%s\"\n", text);
		break;
	}
	fflush(stderr);
}

#ifdef __MINGW32__
#define LOG_TO_FILE
#endif

#ifdef LOG_TO_FILE
#include <stdarg.h>
static void
log_to_file(const char *format, ...)
{
	FILE *logfile;
	static char *logfile_str = 0;
	va_list args;
	char buf[256];
	time_t log_clock;

	if (!rfbEnableClientLogging)
		return;

	if (logfile_str == 0)
	{
		logfile_str = getenv("VNCLOG");
		if (logfile_str == 0)
			logfile_str = "vnc.log";
	}

	logfile = fopen(logfile_str, "a");

	va_start(args, format);

	time(&log_clock);
	strftime(buf, 255, "%d/%m/%Y %X ", localtime(&log_clock));
	fprintf(logfile, buf);

	vfprintf(logfile, format, args);
	fflush(logfile);

	va_end(args);
	fclose(logfile);
}
#endif

static void cleanup(rfbClient *cl)
{
	/*
		just in case we're running in listenLoop:
		close viewer window by restarting SDL video subsystem
	*/
	SDL_QuitSubSystem(SDL_INIT_VIDEO);
	SDL_InitSubSystem(SDL_INIT_VIDEO);
	if (cl)
		rfbClientCleanup(cl);
}

static rfbBool handleSDLEvent(rfbClient *cl, SDL_Event *e)
{
	switch (e->type)
	{
	case SDL_WINDOWEVENT:
		switch (e->window.event)
		{
		case SDL_WINDOWEVENT_EXPOSED:
			SendFramebufferUpdateRequest(cl, 0, 0,
										 cl->width, cl->height, FALSE);
			break;
		case SDL_WINDOWEVENT_FOCUS_GAINED:
			if (SDL_HasClipboardText())
			{
				char *text = SDL_GetClipboardText();
				if (text)
				{
					rfbClientLog("sending clipboard text '%s'\n", text);
					SendClientCutText(cl, text, strlen(text));
				}
			}

			break;
		case SDL_WINDOWEVENT_FOCUS_LOST:
			if (rightAltKeyDown)
			{
				SendKeyEvent(cl, XK_Alt_R, FALSE);
				rightAltKeyDown = FALSE;
				rfbClientLog("released right Alt key\n");
			}
			if (leftAltKeyDown)
			{
				SendKeyEvent(cl, XK_Alt_L, FALSE);
				leftAltKeyDown = FALSE;
				rfbClientLog("released left Alt key\n");
			}
			break;
		}
		break;
	case SDL_MOUSEWHEEL:
	{
		int steps;
		if (viewOnly)
			break;

		if (e->wheel.y > 0)
			for (steps = 0; steps < e->wheel.y; ++steps)
			{
				SendPointerEvent(cl, x, y, rfbButton4Mask);
				SendPointerEvent(cl, x, y, 0);
			}
		if (e->wheel.y < 0)
			for (steps = 0; steps > e->wheel.y; --steps)
			{
				SendPointerEvent(cl, x, y, rfbButton5Mask);
				SendPointerEvent(cl, x, y, 0);
			}
		if (e->wheel.x > 0)
			for (steps = 0; steps < e->wheel.x; ++steps)
			{
				SendPointerEvent(cl, x, y, 0b01000000);
				SendPointerEvent(cl, x, y, 0);
			}
		if (e->wheel.x < 0)
			for (steps = 0; steps > e->wheel.x; --steps)
			{
				SendPointerEvent(cl, x, y, 0b00100000);
				SendPointerEvent(cl, x, y, 0);
			}
		break;
	}
	case SDL_MOUSEBUTTONUP:
	case SDL_MOUSEBUTTONDOWN:
	case SDL_MOUSEMOTION:
	{
		int state, i;
		if (viewOnly)
			break;

		if (e->type == SDL_MOUSEMOTION)
		{
			x = e->motion.x;
			y = e->motion.y;
			state = e->motion.state;
		}
		else
		{
			x = e->button.x;
			y = e->button.y;
			state = e->button.button;
			for (i = 0; buttonMapping[i].sdl; i++)
				if (state == buttonMapping[i].sdl)
				{
					state = buttonMapping[i].rfb;
					if (e->type == SDL_MOUSEBUTTONDOWN)
						buttonMask |= state;
					else
						buttonMask &= ~state;
					break;
				}

				// SendFramebufferUpdateRequest(cl, x-10 > 0 ? x-10 : 0, y-10 > 0 ? y-10 : 0, 20, 20, TRUE);
			// SendFramebufferUpdateRequest(cl, x, y, 2, 2, FALSE);
			SendFramebufferUpdateRequest(cl, x-5 > 0 ? x-5 : 0 , y-5 > 0 ? y-5 : 0, x+5 < cl->width ? x+5 : cl->width-x, y+5 < cl->height ? y+5 : cl->height-y, TRUE);
			ping_r.x = x-5 > 0 ? x-5 : 0;
			ping_r.y = y-5 > 0 ? y-5 : 0;
			ping_r.w = x+5 < cl->width ? x+5 : cl->width-x;
			ping_r.h = y+5 < cl->height ? y+5 : cl->height-y;
			before = clock();
		}
		// Send buffer request first as it takes longer to complete

		// Request update for 20x20 pixel frame around mouse action

		SendPointerEvent(cl, x, y, buttonMask);
		buttonMask &= ~(rfbButton4Mask | rfbButton5Mask);
		// SendFramebufferUpdateRequest(cl, x-10 > 0 ? x-10 : 0, y-10 > 0 ? y-10 : 0, 20, 20, TRUE);
		break;
	}
	case SDL_KEYUP:
	case SDL_KEYDOWN:
		if (viewOnly)
			break;
		SendKeyEvent(cl, SDL_key2rfbKeySym(&e->key),
					 e->type == SDL_KEYDOWN ? TRUE : FALSE);
		if (e->key.keysym.sym == SDLK_RALT)
			rightAltKeyDown = e->type == SDL_KEYDOWN;
		if (e->key.keysym.sym == SDLK_LALT)
			leftAltKeyDown = e->type == SDL_KEYDOWN;
		break;
	case SDL_TEXTINPUT:
		if (viewOnly)
			break;
		rfbKeySym sym = utf8char2rfbKeySym(e->text.text);
		SendKeyEvent(cl, sym, TRUE);
		SendKeyEvent(cl, sym, FALSE);
		break;
	case SDL_QUIT:
		if (listenLoop)
		{
			cleanup(cl);
			return FALSE;
		}
		else
		{
			rfbClientCleanup(cl);
			exit(0);
		}
	default:
		rfbClientLog("ignore SDL event: 0x%x\n", e->type);
	}
	return TRUE;
}

static void got_selection(rfbClient *cl, const char *text, int len)
{
	rfbClientLog("received clipboard text '%s'\n", text);
	if (SDL_SetClipboardText(text) != 0)
		rfbClientErr("could not set received clipboard text: %s\n", SDL_GetError());
}

static rfbCredential *get_credential(rfbClient *cl, int credentialType)
{
	rfbCredential *c = malloc(sizeof(rfbCredential));
	c->userCredential.username = malloc(RFB_BUF_SIZE);
	c->userCredential.password = malloc(RFB_BUF_SIZE);

	if (credentialType != rfbCredentialTypeUser)
	{
		rfbClientErr("something else than username and password required for authentication\n");
		return NULL;
	}

	rfbClientLog("username and password required for authentication!\n");
	printf("user: ");
	fgets(c->userCredential.username, RFB_BUF_SIZE, stdin);
	printf("pass: ");
	fgets(c->userCredential.password, RFB_BUF_SIZE, stdin);

	/* remove trailing newlines */
	c->userCredential.username[strcspn(c->userCredential.username, "\n")] = 0;
	c->userCredential.password[strcspn(c->userCredential.password, "\n")] = 0;

	return c;
}

static void *SDL_EventLoop(void *vargp)
{
	SDL_Event e;
	rfbClient *cl = (rfbClient*)vargp;
	while(1)
	{
		if (SDL_PollEvent(&e))
		{
			/*
				handleSDLEvent() return 0 if user requested window close.
				In this case, handleSDLEvent() will have called cleanup().
			*/
			if (!handleSDLEvent(cl, &e))
				break;
		}
		else
		{
			usleep(300);
		}
	}
}

static void initAppData(AppData* data) {
	data->shareDesktop=TRUE;
	data->viewOnly=FALSE;
	data->encodingsString="tight copyrect zlib hextile raw";
	data->useBGR233=FALSE;
	data->nColours=0;
	data->forceOwnCmap=FALSE;
	data->forceTrueColour=FALSE;
	data->requestedDepth=0;
	data->compressLevel=3;
	data->qualityLevel=5;
	data->enableJPEG=TRUE;
	data->useRemoteCursor=TRUE;
}

static void setEncodings(rfbClient *cl) {
	SetServer2Client(cl, rfbEncodingTight);
	SetServer2Client(cl, rfbEncodingZlib);
	SetServer2Client(cl, rfbEncodingCompressLevel3);
	SetServer2Client(cl, rfbEncodingCopyRect);

	SetClient2Server(cl, rfbEncodingTight);
	SetClient2Server(cl, rfbEncodingZlib);
	SetClient2Server(cl, rfbEncodingCompressLevel3);
	SetClient2Server(cl, rfbEncodingCopyRect);
}


int main(int argc, char **argv)
{
	rfbClient *cl;
	int i, j;
	SDL_Event e;

#ifdef LOG_TO_FILE
	rfbClientLog = rfbClientErr = log_to_file;
#endif

	for (i = 1, j = 1; i < argc; i++)
		if (!strcmp(argv[i], "-viewonly"))
			viewOnly = 1;
		else if (!strcmp(argv[i], "-resizable"))
			enableResizable = 1;
		else if (!strcmp(argv[i], "-no-resizable"))
			enableResizable = 0;
		else if (!strcmp(argv[i], "-listen"))
		{
			listenLoop = 1;
			argv[i] = "-listennofork";
			++j;
		}
		else
		{
			if (i != j)
				argv[j] = argv[i];
			j++;
		}
	argc = j;

	SDL_Init(SDL_INIT_VIDEO | SDL_INIT_NOPARACHUTE);
	atexit(SDL_Quit);
	signal(SIGINT, exit);
	signal(SIGKILL, exit);

	do
	{
		/* 16-bit: cl=rfbGetClient(5,3,2); */
		// cl = rfbGetClient(8, 3, 4);
		cl = rfbGetClient(5, 3, 2);
		initAppData(&cl->appData);
		// setEncodings(cl);
		cl->MallocFrameBuffer = resize;
		cl->canHandleNewFBSize = TRUE;
		cl->GotFrameBufferUpdate = update;
		cl->GotCopyRect = update_copyrect;
		cl->HandleKeyboardLedState = kbd_leds;
		cl->HandleTextChat = text_chat;
		cl->GotXCutText = got_selection;
		cl->GetCredential = get_credential;
		cl->listenPort = LISTEN_PORT_OFFSET;
		cl->listen6Port = LISTEN_PORT_OFFSET;
		cl->major = 3;
		cl->minor = 5;
		cl->canUseHextile = TRUE;
		// Init tight
		cl->raw_buffer_size = -1;
  		cl->decompStreamInited = FALSE;

		memset(cl->zlibStreamActive,0,sizeof(rfbBool)*4);
		
		if (pthread_mutex_init(&render_lock, NULL) != 0)
		{
			printf("\n mutex init failed\n");
			return 1;
		}

		if (!rfbInitClient(cl, &argc, argv))
		{
			cl = NULL; /* rfbInitClient has already freed the client struct */
			cleanup(cl);
			break;
		}

		pthread_t render_thread_id; 
		pthread_t sdl_event_thread_id; 
		printf("Initialize render thread\n"); 
		pthread_create(&render_thread_id, NULL, render_screen, (void*)cl);
		
		pthread_create(&sdl_event_thread_id, NULL, SDL_EventLoop, (void*)cl);

		while (1)
		{

			// i = WaitForMessage(cl, 500);
			i = WaitForMessage(cl, 0);
			if (i < 0)
			{
				cleanup(cl);
				break;
			}
			if (i)
			{
				if (!HandleRFBServerMessage(cl))
				{
					cleanup(cl);
					break;
				}
			}

			// if (SDL_PollEvent(&e))
			// {
			// 	/*
			// 		handleSDLEvent() return 0 if user requested window close.
			// 		In this case, handleSDLEvent() will have called cleanup().
	      	// 	*/
			// 	if (!handleSDLEvent(cl, &e))
			// 		break;
			// }
			// else
			// {
			// 	i = WaitForMessage(cl, 500);
			// 	if (i < 0)
			// 	{
			// 		cleanup(cl);
			// 		break;
			// 	}
			// 	if (i)
			// 	{
			// 		if (!HandleRFBServerMessage(cl))
			// 		{
			// 			cleanup(cl);
			// 			break;
			// 		}
			// 	}
			// }
		}
	} while (listenLoop);

	pthread_mutex_destroy(&render_lock);

	return 0;
}
