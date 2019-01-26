# sclbot
Telegram schedule bot for MIREA university

*Run docker container:*
```
docker run -e BOT_TOKEN='your bot token' [container id]
```

*Run docker container with custom schedule api url (default: localhost:9000) run:*
```
docker run -e BOT_TOKEN='your bot token' -e SCL_API='url:port' [container id]
```

*To provide database for bot run:*
```
docker run -e BOT_TOKEN='your bot token' -v ~/local/path/data.sqlite:/assets/data.sqlite [container id]
```

*To use proxy server run:*
```
docker run -e BOT_TOKEN='your bot token' -e PROXY='ip:port;username;password' [container id]
```
