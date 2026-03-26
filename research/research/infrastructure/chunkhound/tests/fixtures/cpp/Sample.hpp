#pragma once

#include <memory>
#include <string>

// Header-only utility macros
#define DECLARE_GETTER(type, name) \
    const type& get##name() const { return name##_; }

#define DECLARE_SETTER(type, name) \
    void set##name(const type& value) { name##_ = value; }

namespace Examples {
    // Forward declarations
    class Widget;
    class Button;

    // Type aliases
    using WidgetPtr = std::unique_ptr<Widget>;
    using ButtonPtr = std::unique_ptr<Button>;

    // Template declaration
    template<typename T>
    class Container;

    // Scoped enum
    enum class LogLevel : int {
        DEBUG = 0,
        INFO = 1,
        WARNING = 2,
        ERROR = 3
    };

    // Abstract base class
    class Widget {
    public:
        explicit Widget(const std::string& name);
        virtual ~Widget() = default;

        // Pure virtual function
        virtual void render() const = 0;
        virtual void update(double deltaTime) = 0;

        // Regular virtual function
        virtual std::string getType() const { return "Widget"; }

        // Non-virtual functions
        const std::string& getName() const;
        void setName(const std::string& name);

    protected:
        std::string name_;
        bool visible_;
    };

    // Template class declaration
    template<typename T>
    class EventHandler {
    public:
        using EventCallback = std::function<void(const T&)>;

        EventHandler() = default;
        virtual ~EventHandler() = default;

        // Template member function
        template<typename Func>
        void setCallback(Func&& callback) {
            callback_ = std::forward<Func>(callback);
        }

        void trigger(const T& event) {
            if (callback_) {
                callback_(event);
            }
        }

    private:
        EventCallback callback_;
    };

    // Specialized template declaration
    template<>
    class EventHandler<std::string> {
    public:
        void logEvent(const std::string& message);
    };

    // Namespace within namespace
    namespace Utils {
        // Function declarations
        void initialize();
        void cleanup();
        
        // Template function declaration
        template<typename T>
        T clamp(const T& value, const T& min, const T& max);

        // Constexpr function
        constexpr double PI = 3.14159265359;
        
        constexpr double toRadians(double degrees) {
            return degrees * PI / 180.0;
        }
    }

    // Global constants
    extern const int MAX_WIDGETS;
    extern const std::string DEFAULT_THEME;

    // Global function declarations
    WidgetPtr createWidget(const std::string& type, const std::string& name);
    void destroyWidget(WidgetPtr widget);
    
    // Template function declaration
    template<typename T>
    void registerComponent(const std::string& name);
}

// Using alias at file scope
using namespace Examples::Utils;