import React, {useMemo} from "react";
import {StyleSheet, View} from "react-native";
import {useSafeAreaInsets} from "react-native-safe-area-context";

const DEFAULT_EDGES: [Edge, Edge] = ["top", "bottom"];

type Edge = "top" | "bottom";
type Mode = "padding" | "margin";
type TProps = {
  edges?: Edge | [Edge] | [Edge, Edge];
  mode?: Mode;
} & React.ComponentProps<typeof View>;

export const SafeAreaWrapper: React.FC<TProps> = ({
  children,
  style,
  edges = DEFAULT_EDGES,
  mode = "padding",
  ...rest
}) => {
  const insets = useSafeAreaInsets();

  const viewStyles = useMemo(() => {
    const flatStyle = style ? StyleSheet.flatten(style) : {};
    const hasTopSafeArea =
      typeof edges === "string" ? edges === "top" : edges.includes("top");
    const hasBottomSafeArea =
      typeof edges === "string" ? edges === "bottom" : edges.includes("bottom");

    const top = hasTopSafeArea ? insets.top : 0;
    const bottom = hasBottomSafeArea ? insets.bottom : 0;

    const safeAreaStyle =
      mode === "padding"
        ? {
            paddingTop: top,
            paddingBottom: bottom,
          }
        : {
            marginTop: top,
            marginBottom: bottom,
          };

    return [
      style,
      {
        ...flatStyle,
        ...safeAreaStyle,
      },
    ];
  }, [style, edges, insets.top, insets.bottom, mode]);

  return (
    <View {...rest} style={viewStyles}>
      {children}
    </View>
  );
};
