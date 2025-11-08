import React, { useEffect, useState } from 'react';

interface AnimatedCounterProps {
    targetValue: number;
    duration?: number;
    prefix?: string;
    suffix?: string;
    className?: string;
}

const AnimatedCounter: React.FC<AnimatedCounterProps> = ({
    targetValue,
    duration = 2000,
    prefix = "",
    suffix = "",
    className = ""
}) => {
    const [currentValue, setCurrentValue] = useState(0);
    const [hasAnimated, setHasAnimated] = useState(false);

    useEffect(() => {
        if (hasAnimated) return;

        const startTime = Date.now();
        const startValue = 0;

        const animate = () => {
            const now = Date.now();
            const progress = Math.min((now - startTime) / duration, 1);

            // Easing function for smooth animation
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const newValue = startValue + (targetValue - startValue) * easeOutQuart;

            setCurrentValue(newValue);

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                setCurrentValue(targetValue);
                setHasAnimated(true);
            }
        };

        // Small delay before starting animation
        const timer = setTimeout(() => {
            animate();
        }, 500);

        return () => clearTimeout(timer);
    }, [targetValue, duration, hasAnimated]);

    return (
        <span className={className}>
            {prefix}{currentValue.toLocaleString(undefined, {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })}{suffix}
        </span>
    );
};

export default AnimatedCounter;
