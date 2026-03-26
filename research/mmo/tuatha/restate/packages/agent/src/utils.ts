import { Serde, serde, TerminalError } from "@restatedev/restate-sdk";

export const jsonPassThroughSerde: Serde<Uint8Array> = {
  contentType: "application/json",
  serialize: serde.binary.serialize,
  deserialize: serde.binary.deserialize,
};

export function rethrowIfNotTerminal(e: unknown) {
  if (!(e instanceof TerminalError)) {
    throw e;
  }
}
