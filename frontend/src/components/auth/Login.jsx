import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { MapPin, Loader2 } from 'lucide-react';

/**
 * Login Component
 * REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
 */
export const Login = () => {
  const navigate = useNavigate();
  const { login, register } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: ''
  });

  const handleGoogleLogin = () => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + '/map';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(formData.email, formData.password);
      navigate('/map');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await register(formData.email, formData.password, formData.name);
      navigate('/map');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-blue-500 flex items-center justify-center">
              <MapPin className="w-7 h-7 text-white" />
            </div>
            <span className="font-heading text-3xl font-bold tracking-tight text-white uppercase">
              Coords
            </span>
          </div>
          <p className="text-zinc-500 text-sm font-mono uppercase tracking-wider">
            Unified Spatial OS
          </p>
        </div>

        <Card className="bg-[#0a0a0a] border-zinc-800">
          <CardHeader className="pb-4">
            <CardTitle className="font-heading text-xl uppercase tracking-wide text-white">
              Access Control
            </CardTitle>
            <CardDescription className="text-zinc-500 font-mono text-xs">
              Initialize workspace session
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Google OAuth - Primary */}
            <Button
              data-testid="google-login-btn"
              onClick={handleGoogleLogin}
              className="w-full mb-6 bg-white text-black hover:bg-zinc-200 font-mono uppercase tracking-wider text-xs h-11"
            >
              <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Continue with Google
            </Button>

            <div className="relative mb-6">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-zinc-800" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-[#0a0a0a] px-2 text-zinc-600 font-mono">Or</span>
              </div>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 text-red-400 text-sm font-mono">
                {error}
              </div>
            )}

            <Tabs defaultValue="login" className="w-full">
              <TabsList className="grid w-full grid-cols-2 bg-[#121212] mb-4">
                <TabsTrigger value="login" className="font-mono text-xs uppercase data-[state=active]:bg-zinc-800">Login</TabsTrigger>
                <TabsTrigger value="register" className="font-mono text-xs uppercase data-[state=active]:bg-zinc-800">Register</TabsTrigger>
              </TabsList>

              <TabsContent value="login">
                <form onSubmit={handleEmailLogin} className="space-y-4">
                  <div>
                    <Label className="font-mono text-xs uppercase text-zinc-400">Email</Label>
                    <Input
                      data-testid="login-email-input"
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="bg-[#121212] border-zinc-800 font-mono text-sm"
                      placeholder="operator@coords.app"
                      required
                    />
                  </div>
                  <div>
                    <Label className="font-mono text-xs uppercase text-zinc-400">Password</Label>
                    <Input
                      data-testid="login-password-input"
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      className="bg-[#121212] border-zinc-800 font-mono text-sm"
                      placeholder="••••••••"
                      required
                    />
                  </div>
                  <Button
                    data-testid="login-submit-btn"
                    type="submit"
                    disabled={loading}
                    className="w-full bg-blue-500 hover:bg-blue-600 font-mono uppercase tracking-wider text-xs h-10"
                  >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Initialize Session'}
                  </Button>
                </form>
              </TabsContent>

              <TabsContent value="register">
                <form onSubmit={handleRegister} className="space-y-4">
                  <div>
                    <Label className="font-mono text-xs uppercase text-zinc-400">Name</Label>
                    <Input
                      data-testid="register-name-input"
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="bg-[#121212] border-zinc-800 font-mono text-sm"
                      placeholder="Operator Name"
                    />
                  </div>
                  <div>
                    <Label className="font-mono text-xs uppercase text-zinc-400">Email</Label>
                    <Input
                      data-testid="register-email-input"
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="bg-[#121212] border-zinc-800 font-mono text-sm"
                      placeholder="operator@coords.app"
                      required
                    />
                  </div>
                  <div>
                    <Label className="font-mono text-xs uppercase text-zinc-400">Password</Label>
                    <Input
                      data-testid="register-password-input"
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      className="bg-[#121212] border-zinc-800 font-mono text-sm"
                      placeholder="••••••••"
                      required
                    />
                  </div>
                  <Button
                    data-testid="register-submit-btn"
                    type="submit"
                    disabled={loading}
                    className="w-full bg-emerald-500 hover:bg-emerald-600 font-mono uppercase tracking-wider text-xs h-10"
                  >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Create Account'}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        <p className="text-center mt-6 text-zinc-600 text-xs font-mono">
          Protocol: CC0 | Runtime: MIT | Phase 9
        </p>
      </div>
    </div>
  );
};

export default Login;
