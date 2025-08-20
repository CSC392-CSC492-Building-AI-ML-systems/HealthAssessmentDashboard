"use client";

import React, { createContext, useContext, useState, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle, X, AlertTriangle, Info } from "lucide-react";

export type ErrorType = "error" | "warning" | "info";

export interface Toast {
    id: string;
    message: string;
    type: ErrorType;
    title?: string;
    duration?: number;
    dismissible?: boolean;
}

interface ToastContextType {
    showToast: (toast: Omit<Toast, "id">) => void;
    showError: (message: string, title?: string) => void;
    showWarning: (message: string, title?: string) => void;
    showInfo: (message: string, title?: string) => void;
    dismissToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

// Internal ToastMessage component
interface ToastMessageProps {
    message: string;
    type: ErrorType;
    title?: string;
    show: boolean;
    dismissible?: boolean;
    onDismiss?: () => void;
    className?: string;
}

const ToastMessage: React.FC<ToastMessageProps> = ({
    message,
    type = "error",
    show,
    onDismiss,
    dismissible = true,
    className = "",
    title
}) => {
    const getStyles = () => {
        switch (type) {
            case "error":
                return {
                    container: "bg-red-50 border-red-200 text-red-800",
                    icon: "text-red-500",
                    title: "text-red-900"
                };
            case "warning":
                return {
                    container: "bg-yellow-50 border-yellow-200 text-yellow-800",
                    icon: "text-yellow-500",
                    title: "text-yellow-900"
                };
            case "info":
                return {
                    container: "bg-blue-50 border-blue-200 text-blue-800",
                    icon: "text-blue-500",
                    title: "text-blue-900"
                };
            default:
                return {
                    container: "bg-red-50 border-red-200 text-red-800",
                    icon: "text-red-500",
                    title: "text-red-900"
                };
        }
    };

    const getIcon = () => {
        switch (type) {
            case "error":
                return <AlertCircle size={20} />;
            case "warning":
                return <AlertTriangle size={20} />;
            case "info":
                return <Info size={20} />;
            default:
                return <AlertCircle size={20} />;
        }
    };

    const getDefaultTitle = () => {
        switch (type) {
            case "error":
                return "Error";
            case "warning":
                return "Warning";
            case "info":
                return "Information";
            default:
                return "Error";
        }
    };

    const styles = getStyles();
    const displayTitle = title || getDefaultTitle();

    return (
        <AnimatePresence>
            {show && (
                <motion.div
                    initial={{ opacity: 0, height: 0, marginBottom: 0 }}
                    animate={{ opacity: 1, height: "auto", marginBottom: 16 }}
                    exit={{ opacity: 0, height: 0, marginBottom: 0 }}
                    transition={{ duration: 0.3, ease: "easeInOut" }}
                    className={`
                        border rounded-lg p-4 shadow-sm
                        ${styles.container}
                        ${className}
                    `}
                >
                    <div className="flex items-start">
                        <div className={`flex-shrink-0 mr-3 mt-0.5 ${styles.icon}`}>
                            {getIcon()}
                        </div>
                        
                        <div className="flex-1 min-w-0">
                            {title && (
                                <h4 className={`text-sm font-semibold mb-1 ${styles.title}`}>
                                    {displayTitle}
                                </h4>
                            )}
                            
                            <div className="text-sm">
                                {message && message.trim() ? message.split('\n').map((line, index) => (
                                    <div key={index} className={index > 0 ? "mt-1" : ""}>
                                        {line}
                                    </div>
                                )) : 'An error occurred'}
                            </div>
                        </div>

                        {dismissible && onDismiss && (
                            <button
                                onClick={onDismiss}
                                className={`
                                    flex-shrink-0 ml-3 p-1 rounded-md transition-colors
                                    hover:bg-white/20 focus:outline-none focus:ring-2 focus:ring-offset-2
                                    ${type === "error" ? "focus:ring-red-500" : 
                                      type === "warning" ? "focus:ring-yellow-500" : "focus:ring-blue-500"}
                                    ${styles.icon}
                                `}
                                aria-label="Dismiss"
                            >
                                <X size={16} />
                            </button>
                        )}
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

export const useToast = () => {
    const context = useContext(ToastContext);
    if (!context) {
        throw new Error("useToast must be used within a ToastProvider");
    }
    return context;
};

interface ToastProviderProps {
    children: React.ReactNode;
    /** Maximum number of toasts to show at once */
    maxToasts?: number;
    /** Default toast position */
    position?: "top-right" | "top-left" | "bottom-right" | "bottom-left" | "top-center" | "bottom-center";
}

export const ToastProvider: React.FC<ToastProviderProps> = ({ 
    children, 
    maxToasts = 5,
    position = "top-right"
}) => {
    const [toasts, setToasts] = useState<Toast[]>([]);
    const toastIdRef = useRef(0);

    const generateId = useCallback(() => {
        return `toast-${++toastIdRef.current}`;
    }, []);

    const dismissToast = useCallback((id: string) => {
        setToasts(prev => prev.filter(toast => toast.id !== id));
    }, []);

    const showToast = useCallback((toastData: Omit<Toast, "id">) => {
        const id = generateId();
        
        const defaultDuration = toastData.type === "error" ? 8000 : // 8 seconds for errors
                               toastData.type === "warning" ? 6000 : // 6 seconds for warnings  
                               5000; // 5 seconds for info
        
        const toast: Toast = {
            id,
            duration: defaultDuration,
            dismissible: true,
            ...toastData,
        };

        setToasts(prev => {
            const newToasts = [toast, ...prev];
            return newToasts.slice(0, maxToasts);
        });

        if (toast.duration && toast.duration > 0) {
            setTimeout(() => {
                dismissToast(id);
            }, toast.duration);
        }
    }, [generateId, dismissToast, maxToasts]);

    const showError = useCallback((message: string, title?: string) => {
        showToast({ message, type: "error", title });
    }, [showToast]);

    const showWarning = useCallback((message: string, title?: string) => {
        showToast({ message, type: "warning", title });
    }, [showToast]);

    const showInfo = useCallback((message: string, title?: string) => {
        showToast({ message, type: "info", title });
    }, [showToast]);

    const getPositionClasses = () => {
        switch (position) {
            case "top-right":
                return "top-4 right-4";
            case "top-left":
                return "top-4 left-4";
            case "bottom-right":
                return "bottom-4 right-4";
            case "bottom-left":
                return "bottom-4 left-4";
            case "top-center":
                return "top-4 left-1/2 transform -translate-x-1/2";
            case "bottom-center":
                return "bottom-4 left-1/2 transform -translate-x-1/2";
            default:
                return "top-4 right-4";
        }
    };

    return (
        <ToastContext.Provider value={{
            showToast,
            showError,
            showWarning,
            showInfo,
            dismissToast
        }}>
            {children}
            
            {/* Toast Container */}
            <div className={`fixed z-50 ${getPositionClasses()} max-w-sm w-full space-y-2`}>
                <AnimatePresence>
                    {toasts.map((toast) => (
                        <motion.div
                            key={toast.id}
                            initial={{ opacity: 0, y: position.includes("top") ? -50 : 50, scale: 0.9 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: position.includes("top") ? -50 : 50, scale: 0.9 }}
                            transition={{ duration: 0.3, ease: "easeOut" }}
                        >
                            <ToastMessage
                                message={toast.message}
                                type={toast.type}
                                title={toast.title}
                                show={true}
                                dismissible={toast.dismissible}
                                onDismiss={() => dismissToast(toast.id)}
                                className="shadow-lg"
                            />
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>
        </ToastContext.Provider>
    );
};

export default ToastProvider;
