export type CrateFoldState = "closed" | "folding" | "folded" | "unfolding" | "opening" | "open";

/** A record: its cover, drawn by the page, and the cover's width over its height. */
export type CrateRecord = { image: HTMLCanvasElement; aspect: number };

/** A square on the screen, in CSS pixels. */
export type CrateBox = { left: number; top: number; size: number };

export type CrateFoldTextures = {
  "front.png": string;
  "back.png": string;
  "side.png": string;
  "floor.png": string;
};

export type CrateFoldOptions = {
  /** The three module: `await import("three")` */
  THREE: typeof import("three");
  /** Element the canvas is appended to */
  mount: HTMLElement;
  textures: CrateFoldTextures;
  /** Drawing size in CSS pixels. The canvas itself scales to its container. */
  size?: number;
  onState?: (state: CrateFoldState) => void;
  onReady?: () => void;
  /** The untextured parts: edge, shaded edge, latch, latch catch. Defaults to the rust crate's. */
  palette?: [number, number, number, number];
  /**
   * "front": face-on at rest (the icon). "above": lifted throughout, for a crate resting folded.
   * "records": the display crate, painted open-fronted and seen from the records camera. It is
   * the same picture a crate from "above" arrives at after flyTo().
   */
  view?: "front" | "above" | "records";
  /** The colour of a record's edges and back. Unlit, like its cover. */
  recordEdge?: number;
  /** Corner radius of a record, in crate units. Default 30. */
  recordRadius?: number;
  /**
   * What the display crate does with its front wall. "up" (the default) keeps it standing: the
   * crate is still the icon, and the chosen record slides up out of it until its whole face
   * shows over the wall. "down" folds it away and shows the records through the open front.
   */
  front?: "up" | "down";
};

export type CrateFoldHandle = {
  /** Fold or unfold. Returns true when it is now folding. */
  toggle(): boolean;
  /** Jump to a position, 0 closed to 1 folded, without animating. */
  set(position: number): void;
  /** Play the fold to a position over a given time. Resolves when it arrives. */
  play(position: number, ms: number): Promise<void>;
  /** Move the canvas into a full-screen host with the crate still drawn at `rect`. */
  takeover(host: HTMLElement, rect: DOMRect): void;
  /** After takeover: fly down into the crate until its floor fills the screen. */
  dolly(ms: number): Promise<void>;
  /** After takeover: land straight down so a print `width` floor units wide covers `target`. */
  land(target: { cx: number; cy: number; width: number }, width: number, ms: number): Promise<void>;
  /** Pictures lying on the crate's floor, bottom first, in floor units. */
  setPrints(
    prints: { image: HTMLCanvasElement; w: number; h: number; x: number; z: number; rot: number }[],
  ): void;

  /** The display state at once: front wall down, the other three standing. */
  setOpenFront(): void;
  /**
   * From folded flat, raise the right, left and back walls; the front stays down.
   * `to` 0 lowers them again. Takes `presentDuration` ms at its own pace.
   */
  present(ms?: number, to?: 0 | 1): Promise<void>;
  /**
   * Records standing in the crate, first at the front, painted in place with no motion.
   * Throws unless the crate is open-fronted: the side walls sweep the inside as they rise.
   * An empty list takes them out.
   */
  setRecords(records: CrateRecord[]): void;
  /**
   * Put records into a crate already on screen: lowered in from above, upright, back one first,
   * then flipped to `then` (default: the current selection).
   */
  dropRecords(records: CrateRecord[], ms?: number, then?: number): Promise<void>;
  /**
   * Flip to a record. Those in front lean forward over the folded front wall, it stands upright
   * and lifts, those behind lean back. Interruptible: call it as often as the pointer moves.
   * 260ms by default, cubic-bezier(0.2, 0, 0, 1).
   */
  select(index: number, ms?: number): Promise<void>;
  /** The record select() last aimed at. */
  selected(): number;
  /** The record under a point of the screen (clientX, clientY), or -1. */
  pick(clientX: number, clientY: number): number;
  /**
   * After takeover: carry the crate to `to`, bringing the camera down to the records view.
   * With `open` (the default) the walls rise on the way, so it arrives as a display crate.
   */
  flyTo(to: CrateBox, ms: number, options?: { open?: boolean }): Promise<void>;
  /**
   * The canvas box changed size. Pass the new size in CSS pixels. After takeover it re-reads
   * the window instead, so call it from a resize listener too.
   */
  resize(size: number): void;
  /** Change how the records sit and lay them again. Returns the values in force. */
  tune(values?: { gap?: number; lift?: number; backLean?: number; forwardLean?: number }): {
    gap: number; lift: number; backLean: number; forwardLean: number; front: "up" | "down";
    forwardLeanActual: number; liftUnits: number;
  };
  /** For review: paint one instant. Nothing animates. */
  seek(instant: {
    present?: number;
    from?: number;
    to?: number;
    k?: number;
    drop?: number;
    flight?: { to: CrateBox; k: number };
  }): void;
  dispose(): void;
  /** Length of the fold in milliseconds */
  duration: number;
  /** Length of present() at its own pace, in milliseconds */
  presentDuration: number;
};

export function createCrateFold(options: CrateFoldOptions): CrateFoldHandle;
