import {ComponentPropsWithoutRef, ReactNode, useCallback} from "react";
import {Pressable} from "react-native";
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
} from "react-native-reanimated";

interface Props extends ComponentPropsWithoutRef<typeof Pressable> {
  activeScale?: number;
  children: ReactNode;
  onPress?: () => void;
  onPressIn?: () => void;
  onPressOut?: () => void;
}

export function PressableScale({
  children,
  onPressIn,
  onPressOut,
  onPress,
  activeScale = 0.99,
  ...rest
}: Props) {
  const scale = useSharedValue(1);

  const onPressHandler = useCallback(() => {
    onPress?.();
  }, [onPress]);

  const onPressInHandler = useCallback(() => {
    scale.value = withSpring(activeScale);
    onPressIn?.();
  }, [activeScale, onPressIn, scale]);

  const onPressOutHandler = useCallback(() => {
    scale.value = withSpring(1);
    onPressOut?.();
  }, [scale, onPressOut]);

  const styles = useAnimatedStyle(
    () => ({
      transform: [
        {
          scale: scale.value,
        },
      ],
    }),
    [],
  );

  return (
    <Pressable
      {...rest}
      onPress={onPressHandler}
      onPressIn={onPressInHandler}
      onPressOut={onPressOutHandler}>
      <Animated.View style={styles}>{children}</Animated.View>
    </Pressable>
  );
}
