#pragma once

#include <SDL2/SDL.h>
#include <signal.h>
#include <rfb/rfbclient.h>

static rfbKeySym SDL_key2rfbKeySym(SDL_KeyboardEvent *e)
{
	rfbKeySym k = 0;
	SDL_Keycode sym = e->keysym.sym;

	switch (sym)
	{
	case SDLK_BACKSPACE:
		k = XK_BackSpace;
		break;
	case SDLK_TAB:
		k = XK_Tab;
		break;
	case SDLK_CLEAR:
		k = XK_Clear;
		break;
	case SDLK_RETURN:
		k = XK_Return;
		break;
	case SDLK_PAUSE:
		k = XK_Pause;
		break;
	case SDLK_ESCAPE:
		k = XK_Escape;
		break;
	case SDLK_DELETE:
		k = XK_Delete;
		break;
	case SDLK_KP_0:
		k = XK_KP_0;
		break;
	case SDLK_KP_1:
		k = XK_KP_1;
		break;
	case SDLK_KP_2:
		k = XK_KP_2;
		break;
	case SDLK_KP_3:
		k = XK_KP_3;
		break;
	case SDLK_KP_4:
		k = XK_KP_4;
		break;
	case SDLK_KP_5:
		k = XK_KP_5;
		break;
	case SDLK_KP_6:
		k = XK_KP_6;
		break;
	case SDLK_KP_7:
		k = XK_KP_7;
		break;
	case SDLK_KP_8:
		k = XK_KP_8;
		break;
	case SDLK_KP_9:
		k = XK_KP_9;
		break;
	case SDLK_KP_PERIOD:
		k = XK_KP_Decimal;
		break;
	case SDLK_KP_DIVIDE:
		k = XK_KP_Divide;
		break;
	case SDLK_KP_MULTIPLY:
		k = XK_KP_Multiply;
		break;
	case SDLK_KP_MINUS:
		k = XK_KP_Subtract;
		break;
	case SDLK_KP_PLUS:
		k = XK_KP_Add;
		break;
	case SDLK_KP_ENTER:
		k = XK_KP_Enter;
		break;
	case SDLK_KP_EQUALS:
		k = XK_KP_Equal;
		break;
	case SDLK_UP:
		k = XK_Up;
		break;
	case SDLK_DOWN:
		k = XK_Down;
		break;
	case SDLK_RIGHT:
		k = XK_Right;
		break;
	case SDLK_LEFT:
		k = XK_Left;
		break;
	case SDLK_INSERT:
		k = XK_Insert;
		break;
	case SDLK_HOME:
		k = XK_Home;
		break;
	case SDLK_END:
		k = XK_End;
		break;
	case SDLK_PAGEUP:
		k = XK_Page_Up;
		break;
	case SDLK_PAGEDOWN:
		k = XK_Page_Down;
		break;
	case SDLK_F1:
		k = XK_F1;
		break;
	case SDLK_F2:
		k = XK_F2;
		break;
	case SDLK_F3:
		k = XK_F3;
		break;
	case SDLK_F4:
		k = XK_F4;
		break;
	case SDLK_F5:
		k = XK_F5;
		break;
	case SDLK_F6:
		k = XK_F6;
		break;
	case SDLK_F7:
		k = XK_F7;
		break;
	case SDLK_F8:
		k = XK_F8;
		break;
	case SDLK_F9:
		k = XK_F9;
		break;
	case SDLK_F10:
		k = XK_F10;
		break;
	case SDLK_F11:
		k = XK_F11;
		break;
	case SDLK_F12:
		k = XK_F12;
		break;
	case SDLK_F13:
		k = XK_F13;
		break;
	case SDLK_F14:
		k = XK_F14;
		break;
	case SDLK_F15:
		k = XK_F15;
		break;
	case SDLK_NUMLOCKCLEAR:
		k = XK_Num_Lock;
		break;
	case SDLK_CAPSLOCK:
		k = XK_Caps_Lock;
		break;
	case SDLK_SCROLLLOCK:
		k = XK_Scroll_Lock;
		break;
	case SDLK_RSHIFT:
		k = XK_Shift_R;
		break;
	case SDLK_LSHIFT:
		k = XK_Shift_L;
		break;
	case SDLK_RCTRL:
		k = XK_Control_R;
		break;
	case SDLK_LCTRL:
		k = XK_Control_L;
		break;
	case SDLK_RALT:
		k = XK_Alt_R;
		break;
	case SDLK_LALT:
		k = XK_Alt_L;
		break;
	case SDLK_LGUI:
		k = XK_Super_L;
		break;
	case SDLK_RGUI:
		k = XK_Super_R;
		break;
#if 0
	case SDLK_COMPOSE: k = XK_Compose; break;
#endif
	case SDLK_MODE:
		k = XK_Mode_switch;
		break;
	case SDLK_HELP:
		k = XK_Help;
		break;
	case SDLK_PRINTSCREEN:
		k = XK_Print;
		break;
	case SDLK_SYSREQ:
		k = XK_Sys_Req;
		break;
	default:
		break;
	}
	/* SDL_TEXTINPUT does not generate characters if ctrl is down, so handle those here */
	if (k == 0 && sym > 0x0 && sym < 0x100 && e->keysym.mod & KMOD_CTRL)
		k = sym;

	return k;
}


 void
 SetClient2Server(rfbClient* client, int messageType)
 {
   client->supportedMessages.client2server[((messageType & 0xFF)/8)] |= (1<<(messageType % 8));
 }
 
 void
 SetServer2Client(rfbClient* client, int messageType)
 {
   client->supportedMessages.server2client[((messageType & 0xFF)/8)] |= (1<<(messageType % 8));
 }

