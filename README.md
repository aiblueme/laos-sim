# laos-sim

SIM card comparison guide for tourists visiting Laos — Unitel, Lao Telecom, eSIM providers, coverage maps, and buying tips for 2025–2026.

## Live

https://laos-sim.shellnode.lol

## Stack

- Static HTML/CSS/JS (vanilla, no frameworks)
- nginx:alpine container
- Ghost VPS / Docker
- SSL via SWAG + Cloudflare DNS

## Run Locally

Open `index.html` in a browser, or:

    docker build -t laos-sim .
    docker run -p 8080:80 laos-sim

## Deploy

    docker context use vps2
    docker build -t laos-sim .
    docker compose up -d --build

## Data Sources

Content researched from operator websites (Unitel, Lao Telecom, LTC), eSIM provider sites (Airalo, Holafly, Maya), and travel community reports (2025).
Images acquired via icrawler from Bing/Baidu.
