import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export const STATUS_COLORS = {
  available: { bg: 'bg-emerald-500', text: 'text-emerald-500', border: 'border-emerald-500' },
  occupied: { bg: 'bg-red-500', text: 'text-red-500', border: 'border-red-500' },
  maintenance: { bg: 'bg-amber-500', text: 'text-amber-500', border: 'border-amber-500' },
  reserved: { bg: 'bg-blue-500', text: 'text-blue-500', border: 'border-blue-500' },
  enroute: { bg: 'bg-blue-500', text: 'text-blue-500', border: 'border-blue-500' },
  arrived: { bg: 'bg-emerald-500', text: 'text-emerald-500', border: 'border-emerald-500' },
  loading: { bg: 'bg-amber-500', text: 'text-amber-500', border: 'border-amber-500' },
  departed: { bg: 'bg-zinc-500', text: 'text-zinc-500', border: 'border-zinc-500' },
  delayed: { bg: 'bg-red-500', text: 'text-red-500', border: 'border-red-500' }
};

export const formatTimestamp = (timestamp) => {
  if (!timestamp) return '-';
  const date = new Date(timestamp);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export const formatDistance = (km) => {
  if (km === null || km === undefined) return '-';
  return `${km.toFixed(1)} km`;
};

export const formatETA = (minutes) => {
  if (minutes === null || minutes === undefined) return '-';
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
};
