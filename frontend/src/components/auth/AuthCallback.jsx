import { useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { authAPI } from '../../lib/api';
import { Loader2 } from 'lucide-react';

/**
 * AuthCallback - Handles OAuth session exchange
 * REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
 */
export const AuthCallback = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const hasProcessed = useRef(false);

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const processSession = async () => {
      try {
        const hash = location.hash;
        const sessionIdMatch = hash.match(/session_id=([^&]+)/);
        
        if (!sessionIdMatch) {
          navigate('/login', { replace: true });
          return;
        }

        const sessionId = sessionIdMatch[1];
        const response = await authAPI.session(sessionId);
        
        if (response.data.success) {
          navigate('/map', { replace: true, state: { user: response.data.user } });
        } else {
          navigate('/login', { replace: true });
        }
      } catch (err) {
        console.error('Auth callback error:', err);
        navigate('/login', { replace: true });
      }
    };

    processSession();
  }, [location, navigate]);

  return (
    <div className="min-h-screen bg-[#050505] flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-4" />
        <p className="font-mono text-sm text-zinc-400 uppercase tracking-wider">
          Initializing session...
        </p>
      </div>
    </div>
  );
};

export default AuthCallback;
