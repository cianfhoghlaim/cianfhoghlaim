#include <iostream>
#include <vector>
#include <memory>
#include <string>

// Macro example
#define MAX_SIZE 100
#define SQUARE(x) ((x) * (x))

namespace Examples {
    // Forward declaration
    class Widget;

    // Type alias example
    using StringVector = std::vector<std::string>;
    using WidgetPtr = std::unique_ptr<Widget>;

    // Enum class example
    enum class Status {
        ACTIVE,
        INACTIVE,
        PENDING
    };

    // Template class example
    template<typename T>
    class Container {
    private:
        std::vector<T> items_;
        size_t max_size_;

    public:
        Container(size_t max_size = MAX_SIZE) : max_size_(max_size) {}

        // Move constructor
        Container(Container&& other) noexcept 
            : items_(std::move(other.items_)), max_size_(other.max_size_) {}

        // Template member function
        template<typename U>
        void addItem(U&& item) {
            if (items_.size() < max_size_) {
                items_.emplace_back(std::forward<U>(item));
            }
        }

        // Const member function
        const std::vector<T>& getItems() const {
            return items_;
        }

        // Operator overloading
        T& operator[](size_t index) {
            return items_[index];
        }

        // Static member function
        static Container<T> create(size_t size) {
            return Container<T>(size);
        }
    };

    // Namespace within namespace
    namespace Utils {
        // Function template
        template<typename T>
        T square(const T& value) {
            return SQUARE(value);
        }

        // Lambda with auto
        auto multiplier = [](auto x, auto y) { 
            return x * y; 
        };
    }

    // Class with inheritance
    class Widget {
    public:
        Widget(const std::string& name) : name_(name) {}
        virtual ~Widget() = default;

        virtual void render() const = 0;
        
        const std::string& getName() const { return name_; }

    protected:
        std::string name_;
    };

    // Derived class
    class Button : public Widget {
    private:
        bool pressed_;

    public:
        Button(const std::string& name) : Widget(name), pressed_(false) {}

        void render() const override {
            std::cout << "Rendering button: " << name_ << std::endl;
        }

        void press() { pressed_ = true; }
        bool isPressed() const { return pressed_; }
    };

    // Global variable
    static const int DEFAULT_TIMEOUT = 5000;

    // Global function with modern C++ features
    auto createWidget(const std::string& type) -> std::unique_ptr<Widget> {
        if (type == "button") {
            return std::make_unique<Button>("DefaultButton");
        }
        return nullptr;
    }
}

// Using declaration
using namespace Examples;

// Main function with range-based for loop
int main() {
    Container<int> container;
    
    // Range-based for loop with initializer list
    for (const auto& value : {1, 2, 3, 4, 5}) {
        container.addItem(value);
    }

    // Auto type deduction
    auto widget = createWidget("button");
    if (widget) {
        widget->render();
    }

    return 0;
}