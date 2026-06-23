---
title: "Basic Usage | Better Auth"
source: "https://www.better-auth.com/docs/basic-usage"
author:
published:
created: 2025-12-29
description: "Getting started with Better Auth"
tags:
  - "clippings"
---
## Basic Usage

Better Auth provides built-in authentication support for:

- **Email and password**
- **Social provider (Google, GitHub, Apple, and more)**

But also can easily be extended using plugins, such as: [username](https://www.better-auth.com/docs/plugins/username), [magic link](https://www.better-auth.com/docs/plugins/magic-link), [passkey](https://www.better-auth.com/docs/plugins/passkey), [email-otp](https://www.better-auth.com/docs/plugins/email-otp), and more.

## Email & Password

To enable email and password authentication:

auth.ts

```
import { betterAuth } from "better-auth"

export const auth = betterAuth({

    emailAndPassword: {    

        enabled: true

    } 

})
```

### Sign Up

To sign up a user you need to call the client method `signUp.email` with the user's information.

sign-up.ts

By default, the users are automatically signed in after they successfully sign up. To disable this behavior you can set `autoSignIn` to `false`.

auth.ts

```
import { betterAuth } from "better-auth"

export const auth = betterAuth({

    emailAndPassword: {

        enabled: true,

        autoSignIn: false //defaults to true

  },

})
```

### Sign In

To sign a user in, you can use the `signIn.email` function provided by the client.

sign-in

```
const { data, error } = await authClient.signIn.email({

        /**

         * The user email

         */

        email,

        /**

         * The user password

         */

        password,

        /**

         * A URL to redirect to after the user verifies their email (optional)

         */

        callbackURL: "/dashboard",

        /**

         * remember the user session after the browser is closed. 

         * @default true

         */

        rememberMe: false

}, {

    //callbacks

})
```

### Server-Side Authentication

To authenticate a user on the server, you can use the `auth.api` methods.

server.ts

```
import { auth } from "./auth"; // path to your Better Auth server instance

const response = await auth.api.signInEmail({

    body: {

        email,

        password

    },

    asResponse: true // returns a response object instead of data

});
```

## Social Sign-On

Better Auth supports multiple social providers, including Google, GitHub, Apple, Discord, and more. To use a social provider, you need to configure the ones you need in the `socialProviders` option on your `auth` object.

auth.ts

### Sign in with social providers

To sign in using a social provider you need to call `signIn.social`. It takes an object with the following properties:

sign-in.ts

You can also authenticate using `idToken` or `accessToken` from the social provider instead of redirecting the user to the provider's site. See social providers documentation for more details.

## Signout

To signout a user, you can use the `signOut` function provided by the client.

user-card.tsx

```
await authClient.signOut();
```

you can pass `fetchOptions` to redirect onSuccess

user-card.tsx

## Session

Once a user is signed in, you'll want to access the user session. Better Auth allows you to easily access the session data from both the server and client sides.

### Client Side

#### Use Session

Better Auth provides a `useSession` hook to easily access session data on the client side. This hook is implemented using nanostore and has support for each supported framework and vanilla client, ensuring that any changes to the session (such as signing out) are immediately reflected in your UI.

user.tsx

```
import { authClient } from "@/lib/auth-client" // import the auth client

export function User(){

    const { 

        data: session, 

        isPending, //loading state

        error, //error object

        refetch //refetch the session

    } = authClient.useSession() 

    return (

        //...

    )

}
```

index.vue

```
<script setup lang="ts">

import { authClient } from "~/lib/auth-client"

const session = authClient.useSession() 

</script>

<template>

    <div>

        <div>

            <pre>{{ session.data }}</pre>

            <button v-if="session.data" @click="authClient.signOut()">

                Sign out

            </button>

        </div>

    </div>

</template>
```

user.svelte

```
<script lang="ts">

import { authClient } from "$lib/auth-client"; 

const session = authClient.useSession(); 

</script>

<p>

    {$session.data?.user.email}

</p>
```

user.svelte

user.tsx

```
import { authClient } from "~/lib/auth-client"; 

export default function Home() {

    const session = authClient.useSession() 

    return (

        <pre>{JSON.stringify(session(), null, 2)}</pre>

    );

}
```

#### Get Session

If you prefer not to use the hook, you can use the `getSession` method provided by the client.

user.tsx

```
import { authClient } from "@/lib/auth-client" // import the auth client

const { data: session, error } = await authClient.getSession()
```

You can also use it with client-side data-fetching libraries like [TanStack Query](https://tanstack.com/query/latest).

### Server Side

The server provides a `session` object that you can use to access the session data. It requires request headers object to be passed to the `getSession` method.

**Example: Using some popular frameworks**

server.ts

route.ts

index.astro

+page.ts

index.ts

server/session.ts

app/routes/api/index.ts

## Using Plugins

One of the unique features of Better Auth is a plugins ecosystem. It allows you to add complex auth related functionality with small lines of code.

Below is an example of how to add two factor authentication using two factor plugin.

### Server Configuration

To add a plugin, you need to import the plugin and pass it to the `plugins` option of the auth instance. For example, to add two factor authentication, you can use the following code:

auth.ts

```
import { betterAuth } from "better-auth"

import { twoFactor } from "better-auth/plugins"

export const auth = betterAuth({

    //...rest of the options

    plugins: [ 

        twoFactor() 

    ] 

})
```

now two factor related routes and method will be available on the server.

### Migrate Database

After adding the plugin, you'll need to add the required tables to your database. You can do this by running the `migrate` command, or by using the `generate` command to create the schema and handle the migration manually.

generating the schema:

terminal

```
npx @better-auth/cli generate
```

using the `migrate` command:

terminal

```
npx @better-auth/cli migrate
```

### Client Configuration

Once we're done with the server, we need to add the plugin to the client. To do this, you need to import the plugin and pass it to the `plugins` option of the auth client. For example, to add two factor authentication, you can use the following code:

auth-client.ts

```
import { createAuthClient } from "better-auth/client";

import { twoFactorClient } from "better-auth/client/plugins"; 

const authClient = createAuthClient({

    plugins: [ 

        twoFactorClient({ 

            twoFactorPage: "/two-factor" // the page to redirect if a user needs to verify 2nd factor

        }) 

    ] 

})
```

now two factor related methods will be available on the client.

profile.ts

```
import { authClient } from "./auth-client"

const enableTwoFactor = async() => {

    const data = await authClient.twoFactor.enable({

        password // the user password is required

    }) // this will enable two factor

}

const disableTwoFactor = async() => {

    const data = await authClient.twoFactor.disable({

        password // the user password is required

    }) // this will disable two factor

}

const signInWith2Factor = async() => {

    const data = await authClient.signIn.email({

        //...

    })

    //if the user has two factor enabled, it will redirect to the two factor page

}

const verifyTOTP = async() => {

    const data = await authClient.twoFactor.verifyTOTP({

        code: "123456", // the code entered by the user 

        /**

         * If the device is trusted, the user won't

         * need to pass 2FA again on the same device

         */

        trustDevice: true

    })

}
```

Next step: See the [two factor plugin documentation](https://www.better-auth.com/docs/plugins/2fa).

[Edit on GitHub](https://github.com/better-auth/better-auth/blob/canary/docs/content/docs/basic-usage.mdx)