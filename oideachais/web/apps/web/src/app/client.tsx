// app/client.tsx — TanStack Start browser hydration entry
import { hydrateRoot } from "react-dom/client";
import { StartClient } from "@tanstack/react-start";
import { createRouter } from "./router";

const router = createRouter();
hydrateRoot(document, <StartClient router={router} />);
