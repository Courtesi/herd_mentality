import React, { useEffect, useState } from 'react';
import { Logout, ChevronDown, Trash } from "tabler-icons-react";
import { toast } from "react-hot-toast";
import { useAuth } from '../contexts/AuthContext';
import DeleteAccountModal from './DeleteAccountModal';

const ProfileDropdown: React.FC = () => {
    const { user, isAuthenticated, logout } = useAuth();
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

    const handleLogout = async () => {
        try {
            await logout();
            setIsDropdownOpen(false);
            toast.success('Successfully logged out');
        } catch (error) {
            console.log("Error with logout:", error);
            toast.error('Failed to logout');
        }
    };

    const handleDeleteAccount = () => {
        setIsDropdownOpen(false);
        setIsDeleteModalOpen(true);
    };

    useEffect(() => {
        const handleClickOutside = () => {
            if (isDropdownOpen) {
                setIsDropdownOpen(false);
            }
        };

        if (isDropdownOpen) {
            document.addEventListener('click', handleClickOutside);
        }

        return () => {
            document.removeEventListener('click', handleClickOutside);
        };
    }, [isDropdownOpen]);

    if (!isAuthenticated || !user) {
        return null;
    }

    return (
        <div className="fixed top-6 right-6 z-40">
            <div className="relative">
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        setIsDropdownOpen(!isDropdownOpen);
                    }}
                    className="flex items-center gap-3 bg-neutral-800 hover:bg-neutral-700 rounded-full p-2 pr-4 border border-neutral-600 transition-colors cursor-pointer"
                >
                    <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                        {user.profilePictureUrl ? (
                            <img
                                src={user.profilePictureUrl}
                                referrerPolicy="no-referrer"
                                alt="Profile"
                                className="w-8 h-8 rounded-full object-cover"
                            />
                        ) : (
                            user.fullName.charAt(0).toUpperCase()
                        )}
                    </div>

                    <span className="text-white text-sm font-medium max-w-24 truncate">
                        {user.fullName.split(' ')[0]}
                    </span>
                    <ChevronDown
                        size={16}
                        className={`text-neutral-400 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`}
                    />
                </button>

                {isDropdownOpen && (
                    <div className="absolute top-full right-0 mt-2 w-64 bg-neutral-800 border border-neutral-600 rounded-lg shadow-lg py-2">
                        <div className="px-4 py-3 border-b border-neutral-600">
                            <div className="text-white font-medium">{user.fullName}</div>
                            <div className="text-neutral-400 text-sm">{user.email}</div>
                        </div>

                        <div className="py-1">
                            <button
                                onClick={handleDeleteAccount}
                                className="w-full text-left px-4 py-2 text-neutral-300 hover:bg-neutral-700 hover:text-white transition-colors flex items-center gap-3 cursor-pointer"
                            >
                                <Trash size={16} />
                                Delete Account
                            </button>
                            <button
                                onClick={handleLogout}
                                className="w-full text-left px-4 py-2 text-red-400 hover:bg-red-500/10 hover:text-red-300 transition-colors flex items-center gap-3 cursor-pointer"
                            >
                                <Logout size={16} />
                                Log Out
                            </button>
                        </div>
                    </div>
                )}
            </div>

            <DeleteAccountModal
                isOpen={isDeleteModalOpen}
                onClose={() => setIsDeleteModalOpen(false)}
            />
        </div>
    );
};

export default ProfileDropdown;
