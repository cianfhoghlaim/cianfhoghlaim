import Svg, {Path, SvgProps} from "react-native-svg";

export const PlayLogo = (props: SvgProps & {size?: number}) => {
  return (
    <Svg
      width={props.size || 24}
      height={props.size || 24}
      viewBox="0 0 24 24"
      fill="none"
      {...props}>
      <Path
        d="M4.59 22c-.461 0-.841-.168-1.14-.503-.3-.336-.45-.785-.45-1.35V3.841c0-.564.15-1.01.45-1.338C3.748 2.168 4.128 2 4.59 2c.245 0 .48.042.702.126.23.084.476.198.737.343l13.578 7.81c.499.282.856.549 1.07.8.215.252.323.557.323.915 0 .359-.108.664-.323.915-.214.252-.571.522-1.07.812L6.029 21.52c-.261.152-.507.27-.737.354a1.976 1.976 0 01-.703.126z"
        fill={props.color}
      />
    </Svg>
  );
};
