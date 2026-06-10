/**************************************************************************/
/*  GodotModule.h                                                         */
/**************************************************************************/
/* Copyright (c) 2024-2025 Slay GmbH                                      */
/*                                                                        */
/* Permission is hereby granted, free of charge, to any person obtaining  */
/* a copy of this software and associated documentation files (the        */
/* "Software"), to deal in the Software without restriction, including    */
/* without limitation the rights to use, copy, modify, merge, publish,    */
/* distribute, sublicense, and/or sell copies of the Software, and to     */
/* permit persons to whom the Software is furnished to do so, subject to  */
/* the following conditions:                                              */
/*                                                                        */
/* The above copyright notice and this permission notice shall be         */
/* included in all copies or substantial portions of the Software.        */
/*                                                                        */
/* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,        */
/* EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF     */
/* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. */
/* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY   */
/* CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,   */
/* TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE      */
/* SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                 */
/**************************************************************************/

#pragma once

#include <godot_cpp/classes/godot_instance.hpp>
#include <godot_cpp/classes/rendering_native_surface.hpp>

#include <future>
#include <mutex>

struct PlatformData {};

class GodotModule {
	godot::GodotInstance *_instance = nullptr;
	PlatformData *_data = nullptr;

	std::mutex _mutex;

	std::function<void(const char *, bool)> logFunction;

	GodotModule(PlatformData *data) :
			_data(data) {}

public:
	static GodotModule *get_singleton();

	godot::GodotInstance *get_or_create_instance(std::vector<std::string> args);

	godot::GodotInstance *get_instance() {
		std::unique_lock lock(_mutex);
		return _instance;
	}

	void destroy_instance();

	godot::Ref<godot::RenderingNativeSurface> get_main_rendering_surface();

	void *get_main_rendering_layer();

	godot::Callable create_callable(std::function<void(const godot::Variant **, int, godot::Variant &, GDExtensionCallError &)> f);

	double get_content_scale_factor();

	void focus_out();

	void focus_in();

	bool is_paused();

	void pause();

	void resume();

	void appPause();

	void appResume();

	void updateState();

	void registerWindowUpdateCallback(std::string name, void *handle, std::function<void(bool)> f, void *ref);
	void unregisterWindowUpdateCallback(void *handle);

	void updateWindow(std::string name, bool adding);

	void updateWindows(bool adding);

	void runOnGodotThread(std::function<void()> f, bool wait = false);

	void iterate();

	void set_log_callback(std::function<void(const char *, bool)> lf) {
		logFunction = lf;
	}

	void log(const char *l, bool err) {
		if (logFunction) {
			logFunction(l, err);
		}
	}
};
