# LocalDeploy

A tool for continious deployments on local, NATed machines. Uses ngrok and fastapi service to listen for updates from github, fetches updates from git repo, relaunches with docker-compose. Useful for chatbots.

[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/tterb/atomic-design-ui/blob/master/LICENSES)


## Non-Python Dependencies

- Properly configured ngrok
- Tmux
- Docker-Compose
