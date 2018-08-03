# Development environment setup

## Steps
- `npm install -g @vue/cli`
- Create a girder assetstore
- Enable `danesfield-server` plugin
- Copy content from `.env` file and create `.env.local` and update the content properly
- `npm install` on this directory
- `npm run serve` to run the client app


# Production deployment with Girder
- build client with `npm run build`
- move `client/dist` as `/girder/clients/web/static/core3d`
