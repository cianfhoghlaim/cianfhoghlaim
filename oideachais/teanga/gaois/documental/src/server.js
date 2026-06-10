import * as sapper from '@sapper/server';
import compression from 'compression';
import enthusiast from 'enthusiast';
import polka from 'polka';
import { i18n } from 'services/i18n';
import { cookieMaxAge, cookieName, defaultLocale, excludedRoutes, locales } from 'services/i18n/settings';
import { getProtocol } from 'services/http';
import sirv from 'sirv';

const { ANALYTICS_ID, PORT, NODE_ENV, HOSTNAME } = process.env;
const dev = NODE_ENV === 'development';
const maxAge = !dev ? cookieMaxAge : undefined;

polka()
	.use(
		compression({ threshold: 0 }),
		sirv('static', { dev, maxAge: maxAge }),
		enthusiast({
			cookieMaxAge,
			cookieName,
			defaultLocale,
			excludeDocuments: false,
			excludedRoutes,
			locales
		}),
		i18n(),
		sapper.middleware({
			session: (req) => ({
				analyticsId: ANALYTICS_ID,
				locale: req.locale || defaultLocale,
				hostname: HOSTNAME,
				protocol: getProtocol(req)
			})
		})
	)
	.listen(PORT, err => {
		if (err) console.log('error', err);
	});