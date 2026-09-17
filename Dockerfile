FROM inventree/inventree:stable

# Copy custom entrypoint script to map Railway PostgreSQL variables automatically
COPY entrypoint.sh /railway-entrypoint.sh
RUN chmod +x /railway-entrypoint.sh

# Default Cache Settings
ENV INVENTREE_CACHE_ENABLED=True
ENV INVENTREE_CACHE_HOST=inventree-cache
ENV INVENTREE_CACHE_PORT=6379

# Server & Proxy settings
ENV INVENTREE_WEB_PORT=8000
ENV INVENTREE_PLUGINS_ENABLED=True
ENV INVENTREE_AUTO_UPDATE=True

ENTRYPOINT ["/railway-entrypoint.sh"]
