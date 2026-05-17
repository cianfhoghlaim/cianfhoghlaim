---
title: "Pangolin 1.18 - HTTPS Private Resources, Multi-Site Routing, and Alerting"
source: "https://pangolin.net/news/1-18-release"
author:
  - "[[Pangolin]]"
published: 2026-04-29
created: 2026-05-17
description: "Pangolin 1.18 brings HTTPS support for private resources, multi-site high availability routing, uptime tracking, health checks, alert rules, wildcard resources, and more. Let's dig in!"
tags:
  - "clippings"
---
Pangolin 1.18 is a big one. This release adds HTTPS support for private resources, multi-site high-availability routing, uptime tracking, a flexible alerting system, wildcard resources, and more. Let's walk through everything.

## HTTPS on Private Resources

Private HTTP is a new kind of private resource designed for web workloads. It works like a public resource in that it gets a real domain name on your Pangolin-managed domain and traffic flows through a reverse proxy with valid TLS, but it's only reachable when the user has an active Pangolin client connection. Nothing is exposed on the public internet.

When a connected user opens the URL in their browser, Pangolin resolves the name through the tunnel, the site-side reverse proxy terminates TLS using a certificate provisioned by the control plane, and the request is forwarded to your backend. The scheme and destination port are both configurable. If you've been approximating this with aliases and non-standard ports, private HTTP is the cleaner answer!

![](https://cdn.prod.website-files.com/699d90fb38a034f4ca0324da/69f145028d127d0604345389_7035ff61.png)

Read more about [HTTPs on private resources](https://docs.pangolin.net/manage/resources/private/private-http) in the docs.

## Multi-Site Routing (HA) on Private Resources

Private resources now support multiple sites. Attach more than one site connector to a resource and Pangolin routes client traffic through whichever path is best at the time, weighing factors like latency and availability. If a site goes offline, clients automatically fail over to the next available site with no manual reconfiguration needed.

A common pattern is redundant connectors into the same network. Install a Pangolin site on two servers in the same LAN, attach both to your private resource, and you have a resilient path in. One connector goes down and users stay connected through the other.

The one requirement is that every site you attach must have routable access to the resource's destination. Pangolin assumes any site in the list is a valid path to the same backend, so confirm reachability before adding a site. Expect a short gap of a few seconds during failover while the downed site is registered and routing changes propagate to clients.

![](https://cdn.prod.website-files.com/699d90fb38a034f4ca0324da/69f145028d127d0604345380_005b0bc0.png)

Read more about [multi-site routing on private resources](https://docs.pangolin.net/manage/resources/private/multi-site-routing) in the docs.

## Uptime Tracking

Sites and resources now track uptime. You'll see uptime history on site and resource detail pages, giving you a quick at-a-glance view of recent availability. This also serves as the jumping-off point for creating alert rules. More on that below!

![](https://cdn.prod.website-files.com/699d90fb38a034f4ca0324da/69f145028d127d0604345386_014b0aea.png)

## Standalone Health Checks

Pangolin now supports standalone health checks that aren't tied to any resource. Pick a site to run the probe from, give it a target, choose HTTP or TCP, configure your timing and thresholds, and Pangolin continuously checks whether that endpoint is reachable from the site's network.

This is useful for anything you want to monitor but haven't modeled as a Pangolin resource such as a network printer, an IP camera, a PLC, a legacy server. HTTP checks issue a full request and validate the response; TCP checks simply confirm a connection can be established on a given port.

![](https://cdn.prod.website-files.com/699d90fb38a034f4ca0324da/69f145028d127d0604345383_30a47368.png)

Read more about [health checks](https://docs.pangolin.net/manage/alerting/health-checks) in the docs.

## Alert Rules

Alert rules let you subscribe to state changes across sites, resources, and health checks and automatically deliver notifications when something happens. Setup involves three steps: choose a source (what to watch), a trigger (which change should fire the rule), and one or more actions (what to do).

Actions include email to users, roles, or arbitrary addresses; webhooks that POST a JSON payload to any URL; and native integrations with PagerDuty, Opsgenie, ServiceNow, and incident.io. You can stack multiple actions on the same rule.

You can create rules from the Alert rules page under Alerting, or jump directly from a site or resource detail page using the Create alert rule shortcut near the uptime graph.

![](https://cdn.prod.website-files.com/699d90fb38a034f4ca0324da/69f145028d127d060434538c_071db8bf.png)

Read more about [alert rules](https://docs.pangolin.net/manage/alerting/alert-rules) in the docs.

## Wildcard Resources

Public resources now support wildcard subdomains. Set the subdomain field to \* and Pangolin routes every hostname at that level through the same resource and tunnel. Access rules and authentication apply across all matched hostnames, and the original Host header is preserved so downstream systems can continue routing as expected.

Wildcards require TLS certificates that cover \*.your-level, which means DNS-01 validation. HTTP-01 can only prove a single exact hostname. For self-hosted Pangolin, configure Traefik and Let's Encrypt for DNS-01 and set up wildcard DNS records. For Pangolin Cloud, use a domain delegation and Pangolin handles the certificates automatically.

Read more about [wildcard resources](https://docs.pangolin.net/manage/resources/public/wildcard-resources) in the docs.

## General Improvements and Bug Fixes

A handful of smaller but worthwhile additions made it into 1.18 as well:

1. **Import an identity provider across organizations**. Organization-level identity providers can now be shared across organizations. From the Identity Providers table, click Add Identity Provider and choose Import to see providers from other organizations where you're an administrator. Auto-provisioning settings are configured separately per organization since each has its own roles, but the underlying provider configuration is shared.
2. **Quickly see resources associated with a site**. On the sites table, clicking the resource count text or opening the three-dot row menu now takes you directly to the resources table with a filter already applied for that site. The site edit page also now shows a simplified list of resources associated with that site.
3. **Reject pending sites**. Admins can now reject sites from the Pending Sites tab rather than only being able to approve them.

As always, this release also includes various other UI improvements and bug fixes throughout the product.

## Looking Forward

1.18 brings features that connect to each other in meaningful ways: health checks feed into alerting, uptime feeds into alerting, multi-site routing feeds into high availability. We're excited to see how you put it all together!

Give us a star: [https://github.com/fosrl/pangolin](https://github.com/fosrl/pangolin)

Stay tuned!

About Pangolin

Pangolin is an open-source infrastructure company that provides secure, zero trust remote access for teams of all sizes. Built to simplify user workflows and protect critical systems, Pangolin helps companies and individuals connect to their networks, applications, and devices safely without relying on traditional VPNs. With a focus on device security, usability, and transparency, Pangolin empowers organizations to manage access efficiently while keeping their infrastructure secure.