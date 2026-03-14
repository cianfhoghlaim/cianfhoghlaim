---
title: "Set up Pangolin Zero Trust VPN for private networks - Guides & Tutorials"
source: "https://forum.hhf.technology/t/set-up-pangolin-zero-trust-vpn-for-private-networks/4045/9"
author:
  - "[[hhf.technoloy]]"
published: 2025-12-13
created: 2025-12-29
description: "Pangolin Zero-Trust VPN GuideComplete setup guide for private resource access with real-world examples. What is Pangolin VPN?Pangolin 1.13+ introduces Zero-Trust Network Access (ZTNA). Access private resources like S…"
tags:
  - "clippings"
---
[Guides & Tutorials](https://forum.hhf.technology/c/guides-tutorials/52)

## post by hhf.technoloy on Dec 13

## Pinned globally on Dec 13

## post by C8opmBMzz on Dec 17

## post by phil9309 on Dec 18

[![](https://forum.hhf.technology/letter_avatar_proxy/v4/letter/p/f4b2a3/96.png)](https://forum.hhf.technology/u/phil9309)

[phil9309](https://forum.hhf.technology/u/phil9309)

[11d](https://forum.hhf.technology/t/set-up-pangolin-zero-trust-vpn-for-private-networks/4045/4?u=ciansedai "Post date")

Hey there, thank you for your guide, maybe you have an idea for my specific setup. Right now I do use newt to connect my VPS and my homelab. The VPS side has complete access to my homelab network, like your guide, so far so good.

But my homelab is running komodo core. Right now, the komodo periphery agent, which allows me to control pangolin docker stack on the VPS is connected over the VPSs internet IP, which of course forces me to open a port. Since my homelabs IP is dynamic i have the port open to the whole internet, which sucks. I’m now trying to get the “reverse” connection of your guide working. But I’m starting to think that this isn’t intended? The VPS itself, isn’t reachable from any of my homelab clients. I played around with the –native option of newt, where it creates a tun device so I can actually use ip routes to reach the VPS, but I still cant get a connection the the specific port komodo agent is using going. Do you have any idea for this particular setup? Is it possible with the new version of pangolin?

## post by ISeeMangos on Dec 18

[ISeeMangos](https://forum.hhf.technology/u/iseemangos)

[11d](https://forum.hhf.technology/t/set-up-pangolin-zero-trust-vpn-for-private-networks/4045/5?u=ciansedai "Post date")

Thanks a lot for the detailed guide. I was having some trouble trying to set up, and didn’t know why.

I have identified my mistakes, and it works as expected now.

## post by partytimeexcellent 5 days ago

[partytimeexcellent](https://forum.hhf.technology/u/partytimeexcellent)

[5d](https://forum.hhf.technology/t/set-up-pangolin-zero-trust-vpn-for-private-networks/4045/6?u=ciansedai "Post date")

This will be fantastic if they can get a iOS & Android app out. A lot of my remote access needs are on mobile. Any idea if that’s in the works?

## post by hhf.technoloy 5 days ago

[hhf.technoloy](https://forum.hhf.technology/u/hhf.technoloy) Leader

[5d](https://forum.hhf.technology/t/set-up-pangolin-zero-trust-vpn-for-private-networks/4045/7?u=ciansedai "Post date")

I have a different solution till they come out with this feature. Will post here soon.

## post by FlyFox-FR 3 hours ago

[FlyFox-FR](https://forum.hhf.technology/u/flyfox-fr)

[3h](https://forum.hhf.technology/t/set-up-pangolin-zero-trust-vpn-for-private-networks/4045/8?u=ciansedai "Post date")

Question:

Would it be possible to host a pangolin instance on a vps (e.g. hetzner) without a domain pointing to it - and with the new VPN features in pangolin, connect to the private ressources directly with client←→server tunnels?

If i combine this maybe with a free oracle vps - i have no costs at all.

Basically having a self hosted pangolin VPN relay Server, thats easy to setup and maintain for me(beginner). And not having the need of a public domain, maybe having pangolin dashboard on tailscale.

Yes, that is confusing, why not using tailscale in the first place. For me its because of trying to experiment with pangolin and loving the self host aspect of it and for me headscale was not that easy to setup now.

## post by hhf.technoloy 3 hours ago

[hhf.technoloy](https://forum.hhf.technology/u/hhf.technoloy) Leader

[3h](https://forum.hhf.technology/t/set-up-pangolin-zero-trust-vpn-for-private-networks/4045/9?u=ciansedai "Post date")

Nope, not possible. Instead used an alternative solution. Like wgeasy or similar.  
Then internal you can have your own dns server for your names.

This topic is unpinned for you; it will display in regular order

  

### Want to read more? Browse other topics in Guides & Tutorials or view latest topics.

[Powered by Discourse](https://discourse.org/powered-by)