import React, { useEffect, useRef } from 'react';

import { socketRequest } from '../../sockets';
import request from '../../utils/request';

// The minimal SDK a dynamically loaded plugin UI module gets to talk to the backend. Kept intentionally
// small (just the raw RPC call) so plugin bundles don't need to know about the webapp's internal
// `commands` registry -- see documentation/developers/webui-plugins.md for the full contract.
const pluginSdk = {
  call: (_package, plugin, method, kwargs) => socketRequest(_package, plugin, method, kwargs),
};

// Renders webapp UI extensions that plugins ship themselves for a given named slot (e.g. "player").
// Plugins are discovered at runtime (via the `getUiPlugins` RPC call) and their UI bundles are loaded
// with a plain dynamic import() -- no build-time knowledge of them is required here.
const PluginSlot = ({ name }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    let cancelled = false;
    const mounted = [];

    const load = async () => {
      const { result: manifest, error } = await request('getUiPlugins');
      if (error || !manifest) return;

      for (const extension of manifest.filter((ext) => ext.slot === name)) {
        try {
          const module = await import(/* webpackIgnore: true */ extension.url);
          if (cancelled || !containerRef.current) return;

          const el = document.createElement('div');
          el.dataset.plugin = extension.name;
          containerRef.current.appendChild(el);
          module.mount(el, pluginSdk);
          mounted.push({ module, el });
        } catch (loadError) {
          console.error(`[PluginSlot:${name}] Failed to load UI plugin '${extension.name}':`, loadError);
        }
      }
    };

    load();

    return () => {
      cancelled = true;
      mounted.forEach(({ module, el }) => {
        try {
          module.unmount?.(el);
        } catch (unmountError) {
          console.error(`[PluginSlot:${name}] Failed to unmount UI plugin:`, unmountError);
        }
        el.remove();
      });
    };
  }, [name]);

  return <div ref={containerRef} />;
};

export default PluginSlot;
