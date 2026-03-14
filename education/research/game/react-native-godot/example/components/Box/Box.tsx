// Box.tsx
import React, {memo} from "react";
import {View, ViewStyle} from "react-native";

import type {BoxProps} from "./Box.types";

export const Box: React.FC<BoxProps> = memo(
  ({
    children,
    style,

    position,
    top,
    right,
    bottom,
    left,
    zIndex,

    borderCurve,
    borderRadius,
    aspectRatio,

    width,
    height,

    // flex
    flex,
    flexGrow,
    flexShrink,
    flexBasis,
    flexDirection,
    flexWrap,
    justifyContent,
    alignItems,
    alignContent,
    alignSelf,

    // spacing
    padding,
    paddingHorizontal,
    paddingVertical,
    paddingTop,
    paddingRight,
    paddingBottom,
    paddingLeft,

    margin,
    marginHorizontal,
    marginVertical,
    marginTop,
    marginRight,
    marginBottom,
    marginLeft,

    gap,
    rowGap,
    columnGap,

    ...rest
  }) => {
    const inline: ViewStyle = {
      flex,
      flexGrow,
      flexShrink,
      flexBasis: flexBasis as ViewStyle["flexBasis"],
      flexDirection,
      flexWrap,
      justifyContent,
      alignItems,
      alignContent,
      alignSelf,

      position,
      top,
      right,
      bottom,
      left,
      zIndex,

      borderCurve,
      borderRadius,

      width,
      height,

      aspectRatio,

      padding,
      paddingHorizontal,
      paddingVertical,
      paddingTop,
      paddingRight,
      paddingBottom,
      paddingLeft,

      margin,
      marginHorizontal,
      marginVertical,
      marginTop,
      marginRight,
      marginBottom,
      marginLeft,

      gap,
      rowGap,
      columnGap,
    };

    return (
      <View style={[inline, style]} {...rest}>
        {children}
      </View>
    );
  },
);
