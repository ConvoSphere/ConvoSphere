import React, { useState, useEffect, useRef } from "react";
import { Spin } from "antd";
import { useThemeStore } from "../store/themeStore";
import resourceOptimizer from "../utils/resourceOptimizer";
import type { ImageConfig } from "../utils/resourceOptimizer";

interface OptimizedImageProps extends ImageConfig {
  className?: string;
  style?: React.CSSProperties;
  fallback?: string;
  placeholder?: string;
  onLoad?: () => void;
  onError?: (error: Error) => void;
  showLoading?: boolean;
  aspectRatio?: number;
}

const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  width,
  height,
  quality,
  format,
  lazy = true,
  priority = "normal",
  className,
  style,
  fallback,
  placeholder,
  onLoad,
  onError,
  showLoading = true,
  aspectRatio,
  ...props
}) => {
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  const imgRef = useRef<HTMLImageElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [currentSrc, setCurrentSrc] = useState<string>("");

  // Optimize image URL
  const optimizedSrc = resourceOptimizer.optimizeImage({
    src,
    alt,
    width,
    height,
    quality,
    format,
    lazy,
    priority,
  });

  useEffect(() => {
    if (!lazy) {
      setCurrentSrc(optimizedSrc);
    }
  }, [optimizedSrc, lazy]);

  useEffect(() => {
    if (imgRef.current && lazy) {
      resourceOptimizer.lazyLoadImage(imgRef.current, {
        src: optimizedSrc,
        alt,
        width,
        height,
        quality,
        format,
        lazy,
        priority,
      });

      // Listen for load events
      const handleLoad = () => {
        setIsLoading(false);
        setCurrentSrc(optimizedSrc);
        onLoad?.();
      };

      const handleError = () => {
        setIsLoading(false);
        setHasError(true);
        onError?.(new Error(`Failed to load image: ${src}`));
      };

      imgRef.current.addEventListener("load", handleLoad);
      imgRef.current.addEventListener("error", handleError);

      return () => {
        if (imgRef.current) {
          imgRef.current.removeEventListener("load", handleLoad);
          imgRef.current.removeEventListener("error", handleError);
        }
      };
    }
  }, [optimizedSrc, lazy, onLoad, onError, src]);

  const containerStyle: React.CSSProperties = {
    position: "relative",
    display: "inline-block",
    backgroundColor: colors.colorBgElevated,
    borderRadius: "8px",
    overflow: "hidden",
    ...style,
  };

  if (aspectRatio) {
    containerStyle.aspectRatio = aspectRatio.toString();
  }

  const imageStyle: React.CSSProperties = {
    width: "100%",
    height: "100%",
    objectFit: "cover",
    opacity: isLoading ? 0 : 1,
    transition: "opacity 0.3s ease",
  };

  const loadingStyle: React.CSSProperties = {
    position: "absolute",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    color: colors.colorTextSecondary,
  };

  const placeholderStyle: React.CSSProperties = {
    position: "absolute",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    backgroundColor: colors.colorBgElevated,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    color: colors.colorTextSecondary,
    fontSize: "14px",
  };

  // Show error state
  if (hasError && fallback) {
    return (
      <div style={containerStyle} className={className}>
        <img
          src={fallback}
          alt={alt}
          style={imageStyle}
          onLoad={() => setIsLoading(false)}
        />
      </div>
    );
  }

  // Show placeholder
  if (isLoading && placeholder) {
    return (
      <div style={containerStyle} className={className}>
        <div style={placeholderStyle}>{placeholder}</div>
        {showLoading && (
          <div style={loadingStyle}>
            <Spin size="small" />
          </div>
        )}
      </div>
    );
  }

  return (
    <div style={containerStyle} className={className}>
      <img
        ref={imgRef}
        src={currentSrc || (lazy ? undefined : optimizedSrc)}
        alt={alt}
        style={imageStyle}
        data-src={lazy ? optimizedSrc : undefined}
        data-lazy={lazy ? "true" : undefined}
        data-priority={priority}
        {...props}
      />

      {isLoading && showLoading && (
        <div style={loadingStyle}>
          <Spin size="small" />
        </div>
      )}
    </div>
  );
};

export default OptimizedImage;
