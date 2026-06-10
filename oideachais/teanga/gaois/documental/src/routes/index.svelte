<script context='module'>
    import { defaultLocale } from 'services/i18n/settings';

	export async function preload({}, session) {
		return this.redirect(302, `/${session.locale || defaultLocale}/`);
	}
</script>