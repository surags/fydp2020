cordova.define('cordova/plugin_list', function(require, exports, module) {
  module.exports = [
    {
      "id": "cordova-plugin-kiosk.kioskPlugin",
      "file": "plugins/cordova-plugin-kiosk/kiosk.js",
      "pluginId": "cordova-plugin-kiosk",
      "clobbers": [
        "window.KioskPlugin"
      ]
    }
  ];
  module.exports.metadata = {
    "cordova-plugin-whitelist": "1.3.4",
    "cordova-plugin-kiosk": "0.2"
  };
});