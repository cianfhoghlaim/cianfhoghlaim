import React, { useEffect, useRef } from 'react';
import mirador from 'mirador';

const DocumentDetailView = ({ docId, manifestUrl, onClose }) => {
    const miradorInstanceRef = useRef(null);

    useEffect(() => {
        const config = {
            id: 'mirador-viewer',
            windows: [
                {
                    manifestId: manifestUrl,
                    view: 'single',
                    thumbnailNavigationPosition: 'far-bottom',
                },
            ],
            window: {
                allowClose: false,
                allowMaximize: true,
                allowFullscreen: true,
                defaultSideBarPanel: 'canvas',
                sideBarOpenByDefault: false,
                hideWindowTitle: false,
                views: [
                    { key: 'single', behaviors: ['individuals'] },
                    { key: 'book', behaviors: ['paged'] },
                    { key: 'scroll', behaviors: ['continuous'] },
                    { key: 'gallery' },
                ],
            },
            workspace: {
                showZoomControls: true,
                type: 'mosaic',
            },
            workspaceControlPanel: {
                enabled: false,
            },
            thumbnailNavigation: {
                defaultPosition: 'far-bottom',
            },
            osdConfig: {
                crossOriginPolicy: 'Anonymous',
                ajaxWithCredentials: false,
                loadTilesWithAjax: true,
            },
        };

        miradorInstanceRef.current = mirador.viewer(config);

        // Function to click the reset zoom button
        const clickResetZoom = () => {
            const button = document.querySelector('button[aria-label="Reset zoom"]');
            if (button) {
                console.log('✅ Clicking reset zoom button');
                button.click();
                return true;
            }
            console.log('❌ Reset zoom button not found yet');
            return false;
        };

        // Keep trying to click until successful, then stop
        let attempts = 0;
        const maxAttempts = 10;

        const intervalId = setInterval(() => {
            attempts++;
            const success = clickResetZoom();

            if (success || attempts >= maxAttempts) {
                clearInterval(intervalId);
                if (!success) {
                    console.log('⚠️ Failed to find reset zoom button after', maxAttempts, 'attempts');
                }
            }
        }, 300); // Try every 300ms

        return () => {
            clearInterval(intervalId);
        };
    }, [manifestUrl]);

    return (
        <div className="document-detail-view" style={{ position: 'relative', height: '100%', width: '100%' }}>
            <div
                id="mirador-viewer"
                style={{
                    position: 'relative',
                    width: '100%',
                    height: '600px'
                }}
            />
        </div>
    );
};

export default DocumentDetailView;