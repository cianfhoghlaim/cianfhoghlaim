import type {StyleProp, ViewProps, ViewStyle} from "react-native";

export type Spacing =
  | 1
  | 2
  | 4
  | 8
  | 12
  | 16
  | 20
  | 24
  | 28
  | 32
  | 36
  | 40
  | 44
  | 48;

export type BoxProps = {
  borderCurve?: ViewStyle["borderCurve"];
  aspectRatio?: ViewStyle["aspectRatio"];

  width?: ViewStyle["width"];
  height?: ViewStyle["height"];

  position?: ViewStyle["position"];
  top?: ViewStyle["top"];
  right?: ViewStyle["right"];
  bottom?: ViewStyle["bottom"];
  left?: ViewStyle["left"];
  zIndex?: ViewStyle["zIndex"];

  borderRadius?: ViewStyle["borderRadius"];

  children?: React.ReactNode;
  style?: StyleProp<ViewStyle>;

  // flex
  flex?: number;
  flexGrow?: number;
  flexShrink?: number;
  flexBasis?: ViewStyle["flexDirection"];
  flexDirection?: ViewStyle["flexDirection"];
  flexWrap?: ViewStyle["flexWrap"];
  justifyContent?: ViewStyle["justifyContent"];
  alignItems?: ViewStyle["alignItems"];
  alignContent?: ViewStyle["alignContent"];
  alignSelf?: ViewStyle["alignSelf"];

  // spacing (restricted)
  padding?: Spacing;
  paddingHorizontal?: Spacing;
  paddingVertical?: Spacing;
  paddingTop?: Spacing;
  paddingRight?: Spacing;
  paddingBottom?: Spacing;
  paddingLeft?: Spacing;

  margin?: Spacing;
  marginHorizontal?: Spacing;
  marginVertical?: Spacing;
  marginTop?: Spacing;
  marginRight?: Spacing;
  marginBottom?: Spacing;
  marginLeft?: Spacing;

  gap?: Spacing;
  rowGap?: Spacing;
  columnGap?: Spacing;
} & ViewProps;
