/**************************************************************************/
/*  RTNGodotView.mm                                                       */
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

#import <React/RCTLog.h>
#import <React/RCTUIManager.h>

#include <libgodot/libgodot.h>
#include <godot_cpp/classes/display_server_embedded.hpp>
#include <godot_cpp/classes/engine.hpp>
#include <godot_cpp/classes/godot_instance.hpp>
#include <godot_cpp/classes/main_loop.hpp>
#include <godot_cpp/classes/rendering_native_surface.hpp>
#include <godot_cpp/classes/rendering_native_surface_apple.hpp>
#include <godot_cpp/classes/scene_tree.hpp>
#include <godot_cpp/classes/window.hpp>
#include <godot_cpp/core/math.hpp>
#include <godot_cpp/godot.hpp>
#include <godot_cpp/variant/utility_functions.hpp>

#include "GodotModule.h"

#import "RTNGodotView.h"

#import <react/renderer/components/RTNGodotSpec/ComponentDescriptors.h>
#import <react/renderer/components/RTNGodotSpec/EventEmitters.h>
#import <react/renderer/components/RTNGodotSpec/Props.h>
#import <react/renderer/components/RTNGodotSpec/RCTComponentViewHelpers.h>

using namespace facebook::react;

static const int MAX_TOUCH_COUNT = 32;

static NSMutableArray<UIView *> *_views = [NSMutableArray array];
static UIView *_currentView = nil;

@interface RTNGodotView () <RCTRTNGodotViewViewProtocol>
@end
@implementation RTNGodotView {
	NSString *_windowName;
	CALayer *_renderingLayer;
	uint64_t _windowId;
	godot::Ref<godot::RenderingNativeSurface> _nativeSurface;
	std::vector<UITouch *> _touches;
	bool _propsUpdated;
	bool _instanceCallbackRegistered;
	bool _addingGodotView;
}

+ (BOOL)shouldBeRecycled {
	return NO;
}

+ (void)removeMainLayerFromGodotView:(UIView *)view {
	if (![_views containsObject:view]) {
		return;
	}

	CALayer *mainLayer = (__bridge CALayer *)GodotModule::get_singleton()->get_main_rendering_layer();

	if (view == _currentView) {
		if (mainLayer) {
			[mainLayer removeFromSuperlayer];
		}
	}
	[_views removeObject:view];

	if (_views.count > 0) {
		_currentView = [_views lastObject];
		if (mainLayer) {
			[_currentView.layer addSublayer:mainLayer];
			[_currentView setNeedsLayout];
		}
	} else {
		_currentView = nil;
	}
}

+ (CALayer *)addMainLayerToGodotView:(UIView *)view {
	godot::Ref<godot::RenderingNativeSurface> nativeSurface = GodotModule::get_singleton()->get_main_rendering_surface();
	godot::Ref<godot::RenderingNativeSurfaceApple> appleSurface = godot::Object::cast_to<godot::RenderingNativeSurfaceApple>(*nativeSurface);
	CALayer *mainLayer = (__bridge CALayer *)(void *)appleSurface->get_layer();
	if (![_views containsObject:view]) {
		[_views addObject:view];
	}
	if (mainLayer.superlayer != nil) {
		[mainLayer removeFromSuperlayer];
	}

	[view.layer addSublayer:mainLayer];
	[view setNeedsLayout];

	_currentView = view;
	return mainLayer;
}

- (instancetype)init {
	if (self = [super init]) {
		[self setDefaultValues];
	}
	return self;
}

- (void)setDefaultValues {
	while (self.subviews.firstObject) {
		[self.subviews.firstObject removeFromSuperview];
	}
	self.multipleTouchEnabled = YES;

	_renderingLayer = nil;
	_windowId = 0;
	_touches.reserve(MAX_TOUCH_COUNT);
	for (int i = 0; i < MAX_TOUCH_COUNT; ++i) {
		_touches.push_back(nil);
	}
	_propsUpdated = false;
	_instanceCallbackRegistered = false;
	_windowName = @"";
	_addingGodotView = false;
}

//Setter method
- (void)setWindowName:(NSString *)n {
	if (n == nil) {
		n = @"";
	}
	if ([_windowName isEqualToString:n]) {
		return;
	}

	NSLog(@"Setting windowName to: %@", n);
	_windowName = n;
	if (self.superview) {
		// Remove and add again
		[self removeFromGodotView:true unregister:true];
	}
}

//Getter method
- (NSString *)windowName {
	NSLog(@"Returning windowName: %@", _windowName);
	return _windowName;
}

- (void)setNeedsLayout {
	[super setNeedsLayout];
	[self invalidateIntrinsicContentSize];
}

- (CGSize)intrinsicContentSize {
	return [self sizeThatFits:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
}

- (void)deinit {
}

- (void)addToGodotView {
	NSLog(@"RTNGodotView: Adding Godot View: %@, windowName: %@", self, _windowName);

	godot::GodotInstance *instance = GodotModule::get_singleton()->get_instance();

	if (!_instanceCallbackRegistered) {
		GodotModule::get_singleton()->unregisterWindowUpdateCallback((__bridge void *)self);
		std::string newWinName = [_windowName UTF8String];
		GodotModule::get_singleton()->registerWindowUpdateCallback(newWinName, (__bridge void *)self, [self](bool adding) {
			if (adding) {
				dispatch_async(dispatch_get_main_queue(), ^{
					NSLog(@"RTNGodotView: Adding Godot View from Window Update Callback: %@", self);
					[self addToGodotView];
				});
			} else {
				dispatch_async(dispatch_get_main_queue(), ^{
					NSLog(@"RTNGodotView: Removing Godot View from Window Update Callback: %@", self);
					[self removeFromGodotView:false unregister:false];
				});
			} }, nullptr);
		_instanceCallbackRegistered = true;
	}

	if (!instance || !instance->is_started()) {
		// Cannot continue without a Godot instance
		NSLog(@"RTNGodotView: Godot instance not started yet.");
		return;
	}

	if (_windowId > 0 && godot::UtilityFunctions::is_instance_id_valid(_windowId)) {
		NSLog(@"RTNGodotView: Window already configured");
		return;
	}

	_addingGodotView = true;
	if ([@"" isEqualToString:_windowName]) {
		// Set up the main window

		GodotModule::get_singleton()->runOnGodotThread([=]() {
			godot::MainLoop *mainLoop = godot::Engine::get_singleton()->get_main_loop();
			godot::SceneTree *sceneTree = godot::Object::cast_to<godot::SceneTree>(mainLoop);
			if (!sceneTree) {
				NSLog(@"RTNGodotView: Unable to get SceneTree from Godot!");
				return;
			}
			godot::Window *newWindow = sceneTree->get_root();
			dispatch_async(dispatch_get_main_queue(), ^{
				self->_windowId = newWindow->get_instance_id();
				self->_renderingLayer = [RTNGodotView addMainLayerToGodotView:self];
				[self setNeedsLayout];
				self->_addingGodotView = false;
			});
		});

	} else {
		// Subwindow case
		GodotModule::get_singleton()->runOnGodotThread([=]() {
			godot::MainLoop *mainLoop = godot::Engine::get_singleton()->get_main_loop();
			godot::SceneTree *sceneTree = godot::Object::cast_to<godot::SceneTree>(mainLoop);
			if (!sceneTree) {
				NSLog(@"RTNGodotView: Unable to get SceneTree from Godot!");
				return;
			}

			std::string newWinName = [_windowName UTF8String];
			godot::Node *node = sceneTree->get_root()->find_child(godot::String::utf8(newWinName.c_str()), true, false);
			godot::Window *newWindow = godot::Object::cast_to<godot::Window>(node);

			if (!newWindow) {
				NSLog(@"RTNGodotView: Godot Window not valid: 0x%p", newWindow);
				dispatch_async(dispatch_get_main_queue(), ^{
					self->_addingGodotView = false;
				});
				return;
			}

			CGRect screen = [[UIScreen mainScreen] bounds];
			CALayer *newRenderingLayer = nil;

			godot::Ref<godot::RenderingNativeSurfaceApple> appleSurface = godot::RenderingNativeSurfaceApple::create(0);
			newRenderingLayer = (__bridge CALayer *)(void *)appleSurface->get_layer();
			newRenderingLayer.bounds = CGRectMake(0, 0, screen.size.width, screen.size.height);
			newRenderingLayer.position = CGPointMake(0, 0);
			newRenderingLayer.anchorPoint = CGPointMake(0, 0);
			newRenderingLayer.contentsScale = GodotModule::get_singleton()->get_content_scale_factor();

			godot::RenderingNativeSurface *ptr = godot::Object::cast_to<godot::RenderingNativeSurface>(appleSurface.ptr());
			godot::Ref<godot::RenderingNativeSurface> nativeSurface(ptr);

			newWindow->set_visible(true);
			newWindow->set_native_surface(nativeSurface);
			godot::Callable exited_cb = GodotModule::get_singleton()->create_callable([=](const godot::Variant **p_arguments, int p_argcount, godot::Variant &r_return_value, GDExtensionCallError &r_call_error) {
				// Window is now removed, needs relayout
				dispatch_async(dispatch_get_main_queue(), ^{
					if (self->_renderingLayer == newRenderingLayer) {
						[newRenderingLayer removeFromSuperlayer];
						self->_renderingLayer = nil;
					}
					self->_windowId = 0;
					[self setNeedsLayout];
				});
			});
			newWindow->connect("tree_exited", exited_cb);

			dispatch_async(dispatch_get_main_queue(), ^{
				self->_windowId = newWindow->get_instance_id();
				self->_renderingLayer = newRenderingLayer;
				[self.layer addSublayer:self->_renderingLayer];
				[self setNeedsLayout];
				self->_addingGodotView = false;
			});
		});
	}
}

- (void)removeFromGodotView:(bool)addAfter unregister:(bool)unregister {
	NSLog(@"RTNGodotView: Removing Godot View: %@, windowName: %@, addAfter: %d", self, _windowName, addAfter);
	if (_addingGodotView) {
		NSLog(@"RTNGodotView: Adding in progress, rescheduling: %@", self);
		GodotModule::get_singleton()->runOnGodotThread([=]() {
			dispatch_async(dispatch_get_main_queue(), ^{
				[self removeFromGodotView:addAfter unregister:unregister];
			});
		});
	}
	if (unregister) {
		GodotModule::get_singleton()->unregisterWindowUpdateCallback((__bridge void *)self);
		self->_instanceCallbackRegistered = false;
	}
	void (^removeBlock)() = ^() {
		if (![@"" isEqualToString:self->_windowName]) {
			// Only remove if it is not the main window
			if (self->_renderingLayer) {
				if (self->_renderingLayer.superlayer == self.layer) {
					// Only remove, if it is our sublayer
					[self->_renderingLayer removeFromSuperlayer];
				}
			}
		} else {
			// If it is the main window, then request removal from the manager
			[RTNGodotView removeMainLayerFromGodotView:self];
		}
		self->_windowId = 0;
		self->_renderingLayer = nullptr;
		if (addAfter) {
			[self addToGodotView];
		}
	};
	if ([NSThread isMainThread]) {
		removeBlock();
	} else {
		if (!unregister) {
			// This should only happen when the Godot instance is being stopped
			dispatch_sync(dispatch_get_main_queue(), [&removeBlock]() {
				removeBlock();
			});
		} else {
			dispatch_async(dispatch_get_main_queue(), [&removeBlock]() {
				removeBlock();
			});
		}
	}
}

- (void)layoutSubviews {
	godot::GodotInstance *instance = GodotModule::get_singleton()->get_instance();

	if (!instance || !instance->is_started()) {
		// Cannot continue without a Godot instance
		NSLog(@"RTNGodotView: layoutSubviews: No Godot Instance Running");
		return;
	}

	if (!_windowId || !_renderingLayer) {
		NSLog(@"RTNGodotView: layoutSubviews: No window configured");
		return;
	}

	{
		NSLog(@"RTNGodotView: self.contentView.bounds: %@", NSStringFromCGRect(self.bounds));
		NSLog(@"RTNGodotView: self.contentView.layer.bounds: %@", NSStringFromCGRect(self.layer.bounds));
		NSLog(@"RTNGodotView: _renderingLayer.bounds: %@", NSStringFromCGRect(_renderingLayer.bounds));
		NSLog(@"RTNGodotView: self.contentView.layer.frame: %@", NSStringFromCGRect(self.layer.frame));
		NSLog(@"RTNGodotView: self.contentView.frame: %@", NSStringFromCGRect(self.frame));
		NSLog(@"RTNGodotView: _renderingLayer.frame: %@", NSStringFromCGRect(_renderingLayer.frame));

		{
			double contentScaleFactor = GodotModule::get_singleton()->get_content_scale_factor();
			// Make sure that the rendering layer has always at least 10x10 pixel size
			CGRect bounds = CGRectMake(self.layer.bounds.origin.x,
					self.layer.bounds.origin.x,
					godot::MAX(10, self.layer.bounds.size.width),
					godot::MAX(10, self.layer.bounds.size.height));

			_renderingLayer.bounds = bounds;
			NSLog(@"RTNGodotView: _renderingLayer.bounds: %@", NSStringFromCGRect(_renderingLayer.bounds));
			NSLog(@"RTNGodotView: _renderingLayer.frame: %@", NSStringFromCGRect(_renderingLayer.frame));
			GodotModule::get_singleton()->runOnGodotThread([=]() {
				godot::DisplayServerEmbedded *dse = godot::DisplayServerEmbedded::get_singleton();
				if (dse) {
					if (godot::UtilityFunctions::is_instance_id_valid(_windowId)) {
						godot::Object *obj = godot::UtilityFunctions::instance_from_id(_windowId);
						godot::Window *window = godot::Object::cast_to<godot::Window>(obj);
						if (window) {
							dse->resize_window(godot::Vector2i(_renderingLayer.bounds.size.width * contentScaleFactor, _renderingLayer.bounds.size.height * contentScaleFactor), window->get_window_id());
						}
					}
				}
			});
		}
	}
}

- (int)getTouchId:(UITouch *)touch {
	int first = -1;
	for (int i = 0; i < MAX_TOUCH_COUNT; ++i) {
		if (first == -1 && (i >= _touches.size() || _touches[i] == nil)) {
			first = i;
			continue;
		}
		if (_touches[i] == touch) {
			return i;
		}
	}

	if (first != -1) {
		_touches[first] = touch;
		return first;
	}

	return -1;
}

- (void)removeTouchId:(int)touchId {
	_touches[touchId] = nil;
}

- (void)touchesBegan:(NSSet<UITouch *> *)touches
		   withEvent:(UIEvent *)event {
	godot::GodotInstance *instance = GodotModule::get_singleton()->get_instance();

	if (!instance || !instance->is_started()) {
		NSLog(@"RTNGodotView: touchesBegan: No Godot instance started");
		return;
	}
	if (!_windowId) {
		NSLog(@"RTNGodotView: touchesBegan: No window configured");
		return;
	}
	godot::DisplayServerEmbedded *dse = godot::DisplayServerEmbedded::get_singleton();
	if (!dse) {
		NSLog(@"RTNGodotView: touchesBegan: No Godot DisplayServer instance");
		return;
	}
	for (UITouch *touch in touches) {
		int touchId = [self getTouchId:touch];
		if (touchId == -1) {
			continue;
		}
		CGPoint location = [touch locationInView:self];
		if (!CGRectContainsPoint(_renderingLayer.frame, location)) {
			continue;
		}
		location.x -= _renderingLayer.frame.origin.x;
		location.y -= _renderingLayer.frame.origin.y;
		NSUInteger tapCount = touch.tapCount;
		double contentScaleFactor = GodotModule::get_singleton()->get_content_scale_factor();
		GodotModule::get_singleton()->runOnGodotThread([=]() {
			if (godot::UtilityFunctions::is_instance_id_valid(_windowId)) {
				godot::Object *obj = godot::UtilityFunctions::instance_from_id(_windowId);
				godot::Window *window = godot::Object::cast_to<godot::Window>(obj);
				dse->touch_press(touchId, location.x * contentScaleFactor, location.y * contentScaleFactor, true, tapCount > 1, window->get_window_id());
			}
		});
	}
}

- (void)touchesMoved:(NSSet<UITouch *> *)touches
		   withEvent:(UIEvent *)event {
	godot::GodotInstance *instance = GodotModule::get_singleton()->get_instance();

	if (!instance || !instance->is_started()) {
		NSLog(@"RTNGodotView: touchesMoved: No Godot instance started");
		return;
	}
	if (!_windowId) {
		NSLog(@"RTNGodotView: touchesMoved: No window configured");
		return;
	}
	godot::DisplayServerEmbedded *dse = godot::DisplayServerEmbedded::get_singleton();
	if (!dse) {
		NSLog(@"RTNGodotView: touchesMoved: No Godot DisplayServer instance");
		return;
	}
	for (UITouch *touch in touches) {
		int touchId = [self getTouchId:touch];
		if (touchId == -1) {
			continue;
		}
		CGPoint location = [touch locationInView:self];
		if (!CGRectContainsPoint(_renderingLayer.frame, location)) {
			continue;
		}
		location.x -= _renderingLayer.frame.origin.x;
		location.y -= _renderingLayer.frame.origin.y;
		CGPoint prevLocation = [touch previousLocationInView:self];
		if (!CGRectContainsPoint(_renderingLayer.frame, prevLocation)) {
			continue;
		}
		prevLocation.x -= _renderingLayer.frame.origin.x;
		prevLocation.y -= _renderingLayer.frame.origin.y;
		CGFloat alt = touch.altitudeAngle;
		CGVector azim = [touch azimuthUnitVectorInView:self];
		CGFloat force = touch.force;
		CGFloat maximumPossibleForce = touch.maximumPossibleForce;
		double contentScaleFactor = GodotModule::get_singleton()->get_content_scale_factor();
		GodotModule::get_singleton()->runOnGodotThread([=]() {
			if (godot::UtilityFunctions::is_instance_id_valid(_windowId)) {
				godot::Object *obj = godot::UtilityFunctions::instance_from_id(_windowId);
				godot::Window *window = godot::Object::cast_to<godot::Window>(obj);
				dse->touch_drag(
						touchId,
						prevLocation.x * contentScaleFactor,
						prevLocation.y * contentScaleFactor,
						location.x * contentScaleFactor,
						location.y * contentScaleFactor,
						force / maximumPossibleForce,
						godot::Vector2(azim.dx * cos(alt), azim.dy * cos(alt)),
						window->get_window_id());
			}
		});
	}
}

- (void)touchesEnded:(NSSet<UITouch *> *)touches
		   withEvent:(UIEvent *)event {
	godot::GodotInstance *instance = GodotModule::get_singleton()->get_instance();

	if (!instance || !instance->is_started()) {
		NSLog(@"RTNGodotView: touchesEnded: No Godot instance started");
		return;
	}
	if (!_windowId) {
		NSLog(@"RTNGodotView: touchesEnded: No window configured");
		return;
	}
	godot::DisplayServerEmbedded *dse = godot::DisplayServerEmbedded::get_singleton();
	if (!dse) {
		NSLog(@"RTNGodotView: touchesEnded: No Godot DisplayServer instance");
		return;
	}
	for (UITouch *touch in touches) {
		int touchId = [self getTouchId:touch];
		if (touchId == -1) {
			continue;
		}
		[self removeTouchId:touchId];
		CGPoint location = [touch locationInView:self];
		if (!CGRectContainsPoint(_renderingLayer.frame, location)) {
			continue;
		}
		location.x -= _renderingLayer.frame.origin.x;
		location.y -= _renderingLayer.frame.origin.y;
		double contentScaleFactor = GodotModule::get_singleton()->get_content_scale_factor();
		GodotModule::get_singleton()->runOnGodotThread([=]() {
			if (godot::UtilityFunctions::is_instance_id_valid(_windowId)) {
				godot::Object *obj = godot::UtilityFunctions::instance_from_id(_windowId);
				godot::Window *window = godot::Object::cast_to<godot::Window>(obj);
				dse->touch_press(touchId, location.x * contentScaleFactor, location.y * contentScaleFactor, false, false, window->get_window_id());
			}
		});
	}
}

- (void)touchesCancelled:(NSSet<UITouch *> *)touches
			   withEvent:(UIEvent *)event {
	godot::GodotInstance *instance = GodotModule::get_singleton()->get_instance();

	if (!instance || !instance->is_started()) {
		NSLog(@"RTNGodotView: touchesCancelled: No Godot instance started");
		return;
	}
	if (!_windowId) {
		NSLog(@"RTNGodotView: touchesCancelled: No window configured");
		return;
	}
	godot::DisplayServerEmbedded *dse = godot::DisplayServerEmbedded::get_singleton();
	if (!dse) {
		NSLog(@"RTNGodotView: touchesCancelled: No Godot DisplayServer instance");
		return;
	}
	for (UITouch *touch in touches) {
		int touchId = [self getTouchId:touch];
		if (touchId == -1) {
			continue;
		}
		[self removeTouchId:touchId];
		GodotModule::get_singleton()->runOnGodotThread([=]() {
			if (godot::UtilityFunctions::is_instance_id_valid(_windowId)) {
				godot::Object *obj = godot::UtilityFunctions::instance_from_id(_windowId);
				godot::Window *window = godot::Object::cast_to<godot::Window>(obj);
				dse->touches_canceled(touchId, window->get_window_id());
			}
		});
	}
}

- (void)willMoveToSuperview:(UIView *)newSuperview {
	NSLog(@"RTNGodotView: %@ will move to superview %@", self, newSuperview);
	if (newSuperview == nil) {
		[self removeFromGodotView:false unregister:true];
	} else {
		[self addToGodotView];
	}
}

- (void)updateProps:(Props::Shared const &)props oldProps:(Props::Shared const &)oldProps {
	const auto &oldViewProps = *std::static_pointer_cast<RTNGodotViewProps const>(oldProps);
	const auto &newViewProps = *std::static_pointer_cast<RTNGodotViewProps const>(props);

	// Handle your props here
	if ((oldProps == nullptr && props != nullptr) ||
			((oldProps != nullptr && props != nullptr) && (oldViewProps.windowName != newViewProps.windowName))) {
		[self setWindowName:[NSString stringWithUTF8String:newViewProps.windowName.c_str()]];
	}
	//[super updateProps:props oldProps:oldProps];
}

- (void)didMoveToSuperview:(UIView *)newSuperview {
	NSLog(@"RTNGodotView: %@ did move to superview %@", self, newSuperview);
}

+ (ComponentDescriptorProvider)componentDescriptorProvider {
	return concreteComponentDescriptorProvider<RTNGodotViewComponentDescriptor>();
}

@end
