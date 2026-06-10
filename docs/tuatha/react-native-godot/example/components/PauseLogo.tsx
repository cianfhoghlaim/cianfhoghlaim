import * as React from "react";
import Svg, {Path, SvgProps} from "react-native-svg";

export const PauseLogo = (props: SvgProps & {size?: number}) => {
  return (
    <Svg
      width={props.size || 24}
      height={props.size || 24}
      viewBox="0 0 24 24"
      fill="none"
      {...props}>
      <Path
        d="M2 19.232V4.768c0-.867.253-1.545.758-2.034C3.272 2.244 3.974 2 4.864 2h14.272c.89 0 1.588.245 2.094.734.513.49.77 1.167.77 2.034v14.464c0 .859-.257 1.533-.77 2.022-.506.497-1.204.746-2.094.746H4.864c-.89 0-1.592-.249-2.106-.746C2.253 20.764 2 20.09 2 19.232z"
        fill={props.color}
      />
    </Svg>
  );
};
