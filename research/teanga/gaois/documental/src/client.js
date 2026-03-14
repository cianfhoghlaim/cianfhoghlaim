import * as sapper from '@sapper/app';
import { i18nClient } from 'services/i18n';

import '@formatjs/intl-getcanonicallocales/polyfill';
import '@formatjs/intl-pluralrules/polyfill';
import '@formatjs/intl-pluralrules/dist/locale-data/en';
import '@formatjs/intl-pluralrules/dist/locale-data/ga';

i18nClient();

sapper.start({
	target: document.querySelector('#sapper')
});