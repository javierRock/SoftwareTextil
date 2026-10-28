import { useEffect, useState } from 'react';

export function useApi(load, dependencies = []) {
  const [state, setState] = useState({ data: null, loading: true, error: '' });
  const [revision, setRevision] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setState((current) => ({ ...current, loading: true, error: '' }));
    load(controller.signal)
      .then((data) => setState({ data, loading: false, error: '' }))
      .catch((error) => {
        if (error.name !== 'AbortError') setState({ data: null, loading: false, error: error.message });
      });
    return () => controller.abort();
  // `dependencies` belongs to the caller, like the dependency list of useEffect.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...dependencies, revision]);

  return { ...state, reload: () => setRevision((value) => value + 1), setData: (data) => setState({ data, loading: false, error: '' }) };
}
