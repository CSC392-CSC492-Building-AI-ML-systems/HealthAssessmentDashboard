"use client";

import { motion, useMotionTemplate, useMotionValue } from "framer-motion";
import React, { useCallback, useEffect, useRef } from "react";

interface MagicCardProps {
    children?: React.ReactNode;
    className?: string;
    gradientSize?: number;
    gradientColor?: string;
    gradientOpacity?: number;
    gradientFrom?: string;
    gradientTo?: string;
}

export function MagicCard({
    children,
    className,
    gradientSize = 200,
    gradientColor = "#262626",
    gradientOpacity = 0.4,
    gradientFrom = "#9E7AFF",
    gradientTo = "#FE8BBB",
}: MagicCardProps) {
    const cardRef = useRef<HTMLDivElement>(null);
    const mouseX = useMotionValue(-gradientSize);
    const mouseY = useMotionValue(-gradientSize);

    const handleMouseMove = useCallback(
        (e: MouseEvent) => {
            if (cardRef.current) {
                const { left, top } = cardRef.current.getBoundingClientRect();
                const clientX = e.clientX;
                const clientY = e.clientY;
                mouseX.set(clientX - left);
                mouseY.set(clientY - top);
            }
        },
        [mouseX, mouseY],
    );

    const handleMouseOut = useCallback(
        (e: MouseEvent) => {
            if (!e.relatedTarget) {
                document.removeEventListener("mousemove", handleMouseMove);
                mouseX.set(-gradientSize);
                mouseY.set(-gradientSize);
            }
        },
        [handleMouseMove, mouseX, gradientSize, mouseY],
    );

    const handleMouseEnter = useCallback(() => {
        document.addEventListener("mousemove", handleMouseMove);
        mouseX.set(-gradientSize);
        mouseY.set(-gradientSize);
    }, [handleMouseMove, mouseX, gradientSize, mouseY]);

    useEffect(() => {
        document.addEventListener("mousemove", handleMouseMove);
        document.addEventListener("mouseout", handleMouseOut);
        document.addEventListener("mouseenter", handleMouseEnter);

        return () => {
            document.removeEventListener("mousemove", handleMouseMove);
            document.removeEventListener("mouseout", handleMouseOut);
            document.removeEventListener("mouseenter", handleMouseEnter);
        };
    }, [handleMouseEnter, handleMouseMove, handleMouseOut]);

    useEffect(() => {
        mouseX.set(-gradientSize);
        mouseY.set(-gradientSize);
    }, [gradientSize, mouseX, mouseY]);

    return (
        <div ref={cardRef} className={`relative group overflow-hidden rounded-xl ${className}`}>
            <motion.div
                className="pointer-events-none absolute inset-0 z-0 rounded-[inherit] opacity-100 transition duration-300"
                style={{
                    background: useMotionTemplate`
              radial-gradient(${gradientSize}px circle at ${mouseX}px ${mouseY}px,
              ${gradientFrom}, 
              ${gradientTo}, 
              var(--border) 100%)`,
                }}
            />

            <div className="absolute inset-[1px] z-10 rounded-[inherit] backdrop-blur-md border-[3px] border-border" />

            <motion.div
                className="pointer-events-none absolute inset-0 z-20 rounded-[inherit] opacity-0 transition-opacity duration-300 group-hover:opacity-10"
                style={{
                    background: useMotionTemplate`
              radial-gradient(${gradientSize}px circle at ${mouseX}px ${mouseY}px, ${gradientColor}, transparent 100%)`,
                    opacity: gradientOpacity,
                }}
            />

            <div className="relative z-30">{children}</div>
        </div>

    );
}
