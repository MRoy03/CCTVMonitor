"use client";

import { useEffect, useRef } from "react";
import videojs from "video.js";

// @types/video.js's Player type isn't cleanly exportable; declare the
// minimal surface this component actually uses.
interface MinimalPlayer {
  on(event: string, callback: () => void): void;
  currentTime(): number | undefined;
  dispose(): void;
}

export function VideoPlayer({
  src,
  onTimeUpdate,
  overlay,
}: {
  src: string;
  onTimeUpdate?: (currentTime: number) => void;
  overlay?: React.ReactNode;
}) {
  const videoRef = useRef<HTMLDivElement>(null);
  const playerRef = useRef<MinimalPlayer | null>(null);

  useEffect(() => {
    if (!videoRef.current) return;

    const videoElement = document.createElement("video-js");
    videoElement.classList.add("vjs-big-play-centered", "w-full");
    videoRef.current.appendChild(videoElement);

    const player = videojs(videoElement, {
      controls: true,
      fluid: true,
      preload: "auto",
      sources: [{ src, type: "video/mp4" }],
    }) as unknown as MinimalPlayer;
    playerRef.current = player;

    if (onTimeUpdate) {
      player.on("timeupdate", () => onTimeUpdate(player.currentTime() ?? 0));
    }

    return () => {
      player.dispose();
      playerRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [src]);

  return (
    <div className="relative">
      <div ref={videoRef} />
      {overlay}
    </div>
  );
}
