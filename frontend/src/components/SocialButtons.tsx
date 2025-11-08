import React from 'react';
import { BrandGithub, BrandLinkedin, Mail } from "tabler-icons-react";
import { Link } from "react-router-dom";
import { toast } from "react-hot-toast";

interface SocialButtonsProps {
    className?: string;
    size?: 'sm' | 'md' | 'lg';
    gap?: string;
}

const SocialButtons: React.FC<SocialButtonsProps> = ({
    className = "",
    size = 'md',
    gap = 'gap-10'
}) => {
    const sizeClasses = {
        sm: 'scale-150',
        md: 'scale-200',
        lg: 'scale-250'
    };

    const handleEmailCopy = () => {
        navigator.clipboard.writeText('hello@curtischang.dev');
        toast.success("Email copied to clipboard!");
    };

    return (
        <div className={`flex justify-center items-center ${gap} p-2 ${className}`}>
            <Link to="https://www.linkedin.com/in/changcurtis" target="_blank">
                <BrandLinkedin className={`text-gray-50 hover:text-blue-600 ${sizeClasses[size]} cursor-pointer transition-colors duration-200`}/>
            </Link>

            <Link to="https://www.github.com/Courtesi" target="_blank">
                <BrandGithub className={`text-gray-50 hover:text-gray-800 ${sizeClasses[size]} cursor-pointer transition-colors duration-200`}/>
            </Link>

            <Mail
                onClick={handleEmailCopy}
                className={`text-gray-50 hover:text-red-800 ${sizeClasses[size]} cursor-pointer transition-colors duration-200`}
            />
        </div>
    );
};

export default SocialButtons;
