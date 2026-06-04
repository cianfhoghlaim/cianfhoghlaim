/// <reference types="vinxi/types/client" />
import { StartClient } from "@tanstack/react-start/client";
import { hydrateRoot } from "react-dom/client";
import { getRouter } from "./router";

const router = getRouter();

hydrateRoot(document, <StartClient />);
