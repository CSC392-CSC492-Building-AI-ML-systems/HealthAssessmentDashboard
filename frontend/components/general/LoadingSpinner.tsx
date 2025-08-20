"use client";

import React from "react";

interface LoadingSpinnerProps {
    size?: "sm" | "md" | "lg";
    color?: string;
    className?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
    size = "md", 
    color = "currentColor",
    className = ""
}) => {
    const sizeClasses = {
        sm: "w-4 h-4",
        md: "w-6 h-6", 
        lg: "w-8 h-8"
    };

    return (
        <div 
            className={`inline-block animate-spin rounded-full border-2 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite] ${sizeClasses[size]} ${className}`}
            style={{ 
                color,
                borderWidth: size === "sm" ? "2px" : size === "md" ? "2px" : "3px"
            }}
            role="status"
            aria-label="Loading"
        >
            <span className="sr-only">Loading...</span>
        </div>
    );
};

export default LoadingSpinner;
