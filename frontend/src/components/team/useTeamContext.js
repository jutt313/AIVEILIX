import { useEffect, useState } from 'react';
import { teamApi } from '../../api/team';

export function useTeamContext() {
  const [ctx, setCtx] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const token = sessionStorage.getItem('access_token');
    if (!token) {
      setLoading(false);
      return;
    }
    teamApi
      .getMe()
      .then((data) => {
        if (!cancelled) setCtx(data);
      })
      .catch(() => {
        if (!cancelled) setCtx(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return {
    ctx,
    isMember: !!ctx?.is_member,
    isOwner: ctx ? !ctx.is_member : false,
    loading,
  };
}
