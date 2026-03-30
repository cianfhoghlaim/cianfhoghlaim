import { DurableObject } from 'cloudflare:workers';

export class Container extends DurableObject<Env> {
	container: globalThis.Container;

	constructor(ctx: DurableObjectState, env: Env) {
		super(ctx, env);
		this.container = ctx.container!;
		this.ctx.blockConcurrencyWhile(async () => {
			await this.init();
		});
	}

	async init() {
		if (!this.container.running) this.container.start({ enableInternet: true });
	}

	async fetch(req: Request) {
		const url = req.url.replace('https:', 'http:');
		return this.container.getTcpPort(8080).fetch(url, req);
	}
}

export default {
	async fetch(request, env): Promise<Response> {
		const id: DurableObjectId = env.CONTAINER.idFromName('foo');
		const stub = env.CONTAINER.get(id);
		return await stub.fetch(request);
	},
} satisfies ExportedHandler<Env>;
