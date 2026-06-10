/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 *
 * @format
 */

import "setimmediate"; // Required by New Architecture
import React from "react";
import { useEffect } from "react";
import {
  RTNGodot,
  RTNGodotView,
  runOnGodotThread,
} from "@borndotcom/react-native-godot";
import * as FileSystem from "expo-file-system/legacy";
import { Button, StyleSheet, View, Platform } from "react-native";

import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

import * as Device from "expo-device";

const Stack = createNativeStackNavigator();

function initGodot(name) {
  if (RTNGodot.getInstance() != null) {
    console.log("Godot was already initialized.");
    return;
  }
  console.log("Initializing Godot");

  runOnGodotThread(() => {
    "worklet";
    console.log("Running on Godot Thread");

    if (Platform.OS === "android") {
      RTNGodot.createInstance([
        // Uncomment and fill in the correct IP address and port for debugging in the Godot Editor.
        // Check the documentation for the complete procedure.
        // "--remote-debug",
        // "tcp://IP_ADDRESS:6007",
        "--verbose",
        "--path",
        "/" + name,
        "--rendering-driver",
        "opengl3",
        "--rendering-method",
        "gl_compatibility",
        "--display-driver",
        "embedded",
      ]);
    } else {
      let args = [
        // Uncomment and fill in the correct IP address and port for debugging in the Godot Editor.
        // Check the documentation for the complete procedure.
        // "--remote-debug",
        // "tcp://IP_ADDRESS:6007",
        "--verbose",
        "--main-pack",
        FileSystem.bundleDirectory + name + ".pck",
        "--display-driver",
        "embedded",
      ];

      if (Device.isDevice) {
        args.push(
          "--rendering-driver",
          "opengl3",
          "--rendering-method",
          "gl_compatibility"
        );
      } else {
        args.push(
          "--rendering-driver",
          "metal",
          "--rendering-method",
          "mobile"
        );
      }

      RTNGodot.createInstance(args);
    }

    let Godot = RTNGodot.API();
    var v = Godot.Vector2();
    v.x = 1.0;
    v.y = 2.0;
    console.log("Godot Engine initialized:" + v.x + "," + v.y);
    var engine = Godot.Engine;
    console.log("After Engine");
    var sceneTree = engine.get_main_loop();
    console.log("After Main Loop");
    var root = sceneTree.get_root();
    console.log("After Get Root");
  });
}

function pauseGodot(ev: any) {
  RTNGodot.pause();
}

function resumeGodot(ev: any) {
  RTNGodot.resume();
}

function destroyGodot() {
  runOnGodotThread(() => {
    "worklet";
    RTNGodot.destroyInstance();
  });
}

export interface AppController {
  open_window(windowName: string): void;
  close_window(windowName: string): void;
}

const instance = () => {
  "worklet";

  return RTNGodot.getInstance();
};

const appController = () => {
  "worklet";
  if (!instance()) return null;

  const Godot = RTNGodot.API();
  const engine = Godot.Engine;
  const sceneTree = engine.get_main_loop();
  const root = sceneTree.get_root();
  const controller = root.find_child(
    "AppController",
    true,
    false
  ) as AppController;

  if (!controller) return null;

  if (!controller.has_connections("window_status_update")) {
    controller.window_status_update.connect(function (message: string) {
      console.log(message);
    });
  }

  return controller;
};

const App = () => {
  const openSubwindow = function () {
    runOnGodotThread(() => {
      "worklet";
      let controller = appController();
      if (!controller) return;
      controller.open_window("subwindow");
    });
  };

  const closeSubwindow = function () {
    runOnGodotThread(() => {
      "worklet";
      let controller = appController();
      if (!controller) return;
      controller.close_window("subwindow");
    });
  };

  const MainWindow = ({ navigation }) => {
    return (
      <View style={styles.container}>
        <View style={styles.buttonContainer}>
          <Button
            title="Start 1"
            onPress={() => {
              console.log("Starting Godot...");
              initGodot("GodotTest");
            }}
          />
          <Button
            title="Start 2"
            onPress={() => {
              console.log("Starting Godot...");
              initGodot("GodotTest2");
            }}
          />
          <Button
            title="Stop"
            onPress={() => {
              destroyGodot();
            }}
          />
          <Button title="Pause" onPress={pauseGodot} />
          <Button title="Resume" onPress={resumeGodot} />
          <Button
            title="Open Window"
            onPress={() => {
              navigation.navigate("SubWindow", {});
            }}
          />
        </View>
        <View style={styles.godotContainer}>
          <RTNGodotView style={styles.godot} />
        </View>
      </View>
    );
  };

  const SubWindow = ({ navigation, route }) => {
    useEffect(() => {
      openSubwindow();
      return () => {
        closeSubwindow();
      };
    }, []);
    return (
      <View style={styles.container}>
        <View style={styles.buttonContainer}>
          <Button
            title="Close"
            onPress={() => {
              navigation.goBack();
            }}
          />
        </View>
        <View style={styles.godotContainer}>
          <RTNGodotView style={styles.godot} windowName="subwindow" />
        </View>
      </View>
    );
  };

  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="MainWindow">
        <Stack.Screen name="MainWindow" component={MainWindow} />
        <Stack.Screen
          name="SubWindow"
          component={SubWindow}
          options={{
            headerBackVisible: false,
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    flexDirection: "column",
  },
  headerContainer: {
    flex: 1,
    flexDirection: "row",
    backgroundColor: "red",
    padding: 5,
    justifyContent: "center",
    alignItems: "center",
  },
  buttonContainer: {
    flex: 1,
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "center",
    alignItems: "center",
    height: 20,
  },
  headerText: {
    fontSize: 15,
    color: "white",
  },
  headerButton: {
    flex: 2,
    color: "white",
    justifyContent: "center",
    alignItems: "center",
  },
  godotContainer: {
    flex: 8,
    padding: 20,
  },
  testContainer: {
    flex: 2,
    backgroundColor: "darkblue",
    padding: 10,
  },
  godot: {
    flex: 1,
    padding: 0,
    margin: 0,
  },
});

export default App;
