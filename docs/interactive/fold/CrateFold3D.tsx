"use client";

import { useEffect, useRef, useState } from "react";
import type { CrateFoldHandle, CrateFoldState } from "./crate-fold";
import styles from "./CrateFold3D.module.css";

type Props = {
  /** Folder holding front.png, back.png, side.png and floor.png */
  textures?: string;
  /** The flat icon, shown until the scene is ready and if WebGL is missing */
  poster?: string;
  /** Rendered beneath the crate. Motion is never the only feedback channel. */
  showLabel?: boolean;
  className?: string;
};

const LABEL: Record<CrateFoldState, string> = {
  closed: "closed",
  folding: "folding",
  folded: "folded flat",
  unfolding: "unfolding",
};

/**
 * The crate icon, which is the front of a crate. Click it and it folds the
 * way the real one does: front, back, left side, right side.
 *
 * three is imported on the client only, after mount, so it costs nothing
 * until this component is on the page.
 */
export function CrateFold3D({
  textures = "/images/crates/fold",
  poster = "/images/crates/rust.svg",
  showLabel = true,
  className,
}: Props) {
  const mount = useRef<HTMLSpanElement>(null);
  const fold = useRef<CrateFoldHandle | null>(null);
  const [state, setState] = useState<CrateFoldState>("closed");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [THREE, { createCrateFold }] = await Promise.all([
          import("three"),
          import("./crate-fold"),
        ]);
        if (cancelled || !mount.current) return;
        fold.current = createCrateFold({
          THREE,
          mount: mount.current,
          textures: {
            "front.png": `${textures}/front.png`,
            "back.png": `${textures}/back.png`,
            "side.png": `${textures}/side.png`,
            "floor.png": `${textures}/floor.png`,
          },
          onState: setState,
          onReady: () => setReady(true),
        });
      } catch {
        // no WebGL: the poster stays, and it is the icon, so nothing is lost
      }
    })();
    return () => {
      cancelled = true;
      fold.current?.dispose();
      fold.current = null;
    };
  }, [textures]);

  const open = state === "folded" || state === "folding";

  return (
    <div className={className}>
      <button
        type="button"
        className={styles.button}
        aria-pressed={open}
        aria-label={`Crate, ${LABEL[state]}. Activate to ${open ? "unfold" : "fold flat"}.`}
        disabled={!ready}
        onClick={() => fold.current?.toggle()}
      >
        <span className={styles.lift}>
          <span ref={mount} className={styles.stage} data-ready={ready} />
          {!ready && (
            // eslint-disable-next-line @next/next/no-img-element
            <img className={styles.poster} src={poster} alt="" aria-hidden="true" />
          )}
        </span>
      </button>

      {showLabel && (
        <p className={styles.label} aria-live="polite">
          Crate is <b>{LABEL[state]}</b>
          {(state === "closed" || state === "folded") &&
            ` · click to ${open ? "unfold" : "fold"}`}
        </p>
      )}
    </div>
  );
}

export default CrateFold3D;
