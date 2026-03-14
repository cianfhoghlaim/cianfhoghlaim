import {useCallback} from "react";
import {
  LayoutChangeEvent,
  Pressable,
  StyleSheet,
  useWindowDimensions,
} from "react-native";
import Animated, {
  Extrapolation,
  interpolate,
  useAnimatedStyle,
  useSharedValue,
} from "react-native-reanimated";
import {useSafeAreaInsets} from "react-native-safe-area-context";

import {Box} from "./Box";
import {FileLogo} from "./FileLogo";
import {Item} from "./Item";
import {PauseLogo} from "./PauseLogo";
import {PlayLogo} from "./PlayLogo";
import {RestartLogo} from "./RestartLogo";
import {SafeAreaWrapper} from "./SafeAreaWrapper";
import {spring} from "./spring";

const springConfig = {
  response: 0.4,
  dampingFraction: 0.825,
};

interface IProps {
  onRunnerPress: () => void;
  onPenguPress: () => void;
  onPlayPress: () => void;
  onPausePress: () => void;
  onResumePress: () => void;
  children: React.ReactNode;
}

export const Wrapper: React.FC<IProps> = ({
  children,
  onRunnerPress,
  onPenguPress,
  onPlayPress,
  onPausePress,
  onResumePress,
}) => {
  const {height: screenHeight} = useWindowDimensions();
  const {top, bottom} = useSafeAreaInsets();
  const transition = useSharedValue(0);

  const controlsHeight = useSharedValue(0);
  const desiredScale = useSharedValue(1);

  const onControlsLayout = useCallback(
    (e: LayoutChangeEvent) => {
      const controlsHeight = e.nativeEvent.layout.height + bottom + 20;
      desiredScale.value = (screenHeight - controlsHeight - top) / screenHeight;
    },
    [bottom, desiredScale, screenHeight, top],
  );

  const onLongPress = useCallback(() => {
    transition.value = spring(1, springConfig);
  }, [transition]);

  const onPress = useCallback(() => {
    transition.value = spring(0, springConfig);
  }, [transition]);

  const animatedStyles = useAnimatedStyle(
    () => ({
      transform: [
        {
          translateY: interpolate(transition.value, [0, 1], [0, top]),
        },
        {
          scale: interpolate(transition.value, [0, 1], [1, desiredScale.value]),
        },
      ],
    }),
    [top, controlsHeight, screenHeight],
  );

  const animatedButtonStyles = useAnimatedStyle(() => ({
    transform: [
      {
        translateY: interpolate(transition.value, [0, 1], [5, 0]),
      },
    ],
    opacity: interpolate(
      transition.value,
      [0.5, 1],
      [0, 1],
      Extrapolation.CLAMP,
    ),
  }));

  return (
    <Box style={{flex: 1, backgroundColor: "#101010"}} flex={1}>
      <Box style={StyleSheet.absoluteFill}>
        <Animated.View
          style={[
            {flex: 1, justifyContent: "flex-end", alignItems: "center"},
            animatedButtonStyles,
          ]}>
          <Box alignItems="center" onLayout={onControlsLayout} gap={16}>
            <Box flexDirection="row" gap={16}>
              <Item label="Runner.pck" onPress={onRunnerPress}>
                <FileLogo size={16} color="white" />
              </Item>
              <Item label="Pengu.pck" onPress={onPenguPress}>
                <FileLogo size={16} color="white" />
              </Item>
            </Box>
            <Box flexDirection="row" gap={16}>
              <Item label="Play" onPress={onPlayPress}>
                <PlayLogo size={14} color="white" />
              </Item>
              <Item label="Stop" onPress={onPausePress}>
                <PauseLogo size={14} color="white" />
              </Item>
              <Item label="Restart" onPress={onResumePress}>
                <RestartLogo size={16} color="white" />
              </Item>
            </Box>
          </Box>
          <SafeAreaWrapper edges="bottom" />
        </Animated.View>
      </Box>
      <Animated.View
        style={[{flex: 1, transformOrigin: "top"}, animatedStyles]}>
        <Pressable
          style={{flex: 1}}
          onPress={onPress}
          onLongPress={onLongPress}>
          {children}
        </Pressable>
      </Animated.View>
    </Box>
  );
};
