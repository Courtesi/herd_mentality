import React, { useState, useEffect } from 'react';
import { X, Eye, EyeOff, Loader, AlertTriangle } from 'tabler-icons-react';
import { toast } from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/api';

interface DeleteAccountModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const DeleteAccountModal: React.FC<DeleteAccountModalProps> = ({
  isOpen,
  onClose
}) => {
  const { user, logout } = useAuth();
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [confirmText, setConfirmText] = useState('');

  // Reset form when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setPassword('');
      setConfirmText('');
      setShowPassword(false);
      setIsLoading(false);
    }
  }, [isOpen]);

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen && !isLoading) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, isLoading, onClose]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate confirmation text
    if (confirmText !== 'DELETE') {
      toast.error('Please type DELETE to confirm');
      return;
    }

    // Validate password for non-OAuth users
    if (user?.hasPassword && !password) {
      toast.error('Password is required');
      return;
    }

    setIsLoading(true);

    try {
      await apiService.deleteAccountDirect({
        currentPassword: user?.hasPassword ? password : null
      });

      toast.success('Account deleted successfully');

      // Wait a moment for the toast to show, then logout
      setTimeout(async () => {
        await logout();
        onClose();
      }, 1000);

    } catch (error: unknown) {
      console.error('Delete account error:', error);
      const message = error instanceof Error ? error.message : 'Failed to delete account';
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget && !isLoading) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-neutral-800 rounded-lg w-full max-w-md p-6 relative border-2 border-red-500/50">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-neutral-400 hover:text-white transition-colors cursor-pointer"
          disabled={isLoading}
        >
          <X size={20} />
        </button>

        {/* Header with warning icon */}
        <div className="mb-6 text-center">
          <div className="flex justify-center mb-3">
            <div className="bg-red-500/20 rounded-full p-3">
              <AlertTriangle size={32} className="text-red-500" />
            </div>
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">
            Delete Account
          </h2>
          <p className="text-neutral-400 text-sm">
            This action cannot be undone. All your data will be permanently deleted.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Password field - only for users with password */}
          {user?.hasPassword && (
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-neutral-300 mb-1">
                Confirm Your Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  name="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-3 py-2 pr-10 bg-neutral-700 border border-neutral-600 rounded-md text-white placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  placeholder="Enter your password"
                  required
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-neutral-400 hover:text-white"
                  disabled={isLoading}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>
          )}

          {/* OAuth user notice */}
          {user?.isOAuth2User && !user?.hasPassword && (
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-md p-3">
              <p className="text-blue-300 text-sm">
                You signed in with {user.oauthProvider}. No password required.
              </p>
            </div>
          )}

          {/* Confirmation text input */}
          <div>
            <label htmlFor="confirmText" className="block text-sm font-medium text-neutral-300 mb-1">
              Type <span className="font-bold text-red-400">DELETE</span> to confirm
            </label>
            <input
              type="text"
              id="confirmText"
              name="confirmText"
              value={confirmText}
              onChange={(e) => setConfirmText(e.target.value)}
              className="w-full px-3 py-2 bg-neutral-700 border border-neutral-600 rounded-md text-white placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
              placeholder="Type DELETE"
              required
              disabled={isLoading}
            />
          </div>

          {/* Warning text */}
          <div className="bg-red-500/10 border border-red-500/30 rounded-md p-3">
            <p className="text-red-300 text-sm">
              <strong>Warning:</strong> Your account, profile, and all associated data will be permanently deleted.
            </p>
          </div>

          {/* Action buttons */}
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="flex-1 bg-neutral-700 hover:bg-neutral-600 disabled:bg-neutral-800 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-md transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || confirmText !== 'DELETE'}
              className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-red-800 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-md transition-colors flex items-center justify-center cursor-pointer"
            >
              {isLoading ? (
                <>
                  <Loader className="animate-spin mr-2" size={16} />
                  Deleting...
                </>
              ) : (
                'Delete Account'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DeleteAccountModal;