#include "esp_camera.h"
#include <WiFi.h>
#include "esp_http_server.h"

// Replace with your network credentials
const char* ssid = "SEA-Monitor";
const char* password = "fire1234";

// Camera configuration
#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

void startCameraServer();

void setup() {
    Serial.begin(115200);
    // Initialize the camera
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;
    
    // Init with high specs to pre-allocate larger buffers
    if(psramFound()){
        config.frame_size = FRAMESIZE_UXGA; // FRAMESIZE_UXGA or FRAMESIZE_SVGA
        config.jpeg_quality = 10; // 0-63 lower number means higher quality
        config.fb_count = 2; // if more than one, i2s runs in continuous mode. Use only with JPEG
    } else {
        config.frame_size = FRAMESIZE_SVGA;
        config.jpeg_quality = 12; // 0-63 lower number means higher quality
        config.fb_count = 1;
    }
    
    // Camera init
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init failed with error 0x%x", err);
        return;
    }
    
    // Connect to Wi-Fi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");

    // Start camera server
    startCameraServer();

    Serial.printf("Camera Ready! Use 'http://%s' to connect\n", WiFi.localIP().toString().c_str());
}

void loop() {
    // Put your main code here, to run repeatedly
}

void startCameraServer() {
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 80;

    httpd_handle_t server = NULL;
    if (httpd_start(&server, &config) == ESP_OK) {
        httpd_uri_t stream_uri = {
            .uri       = "/",
            .method    = HTTP_GET,
            .handler   = [](httpd_req_t *req) {
                camera_fb_t * fb = NULL;
                esp_err_t res = ESP_OK;

                fb = esp_camera_fb_get();
                if (!fb) {
                    Serial.println("Camera capture failed");
                    httpd_resp_send_500(req);
                    return ESP_FAIL;
                }

                res = httpd_resp_set_type(req, "image/jpeg");
                if (res == ESP_OK) {
                    res = httpd_resp_send(req, (const char *)fb->buf, fb->len);
                }
                esp_camera_fb_return(fb);
                return res;
            },
            .user_ctx  = NULL
        };

        httpd_register_uri_handler(server, &stream_uri);
    }
}
