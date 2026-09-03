import {Text} from "react-native";

import {Box} from "./Box";
import {PressableScale} from "./PressableScale";

interface ItemProps {
  children?: React.ReactNode;
  label: string;
  onPress: () => void;
}

export const Item: React.FC<ItemProps> = ({children, label, onPress}) => {
  return (
    <PressableScale onPress={onPress}>
      <Box
        flexDirection="row"
        alignItems="center"
        gap={4}
        style={{
          backgroundColor: "#212121",
          borderCurve: "continuous",
          overflow: "hidden",
          borderRadius: 16,
          paddingHorizontal: 12,
          paddingVertical: 8,
          // borderRadius: 19,
          // paddingHorizontal: 15,
          // paddingVertical: 10,
          boxShadow: "inset 0px 1.5px 1px 0px #404040",
        }}>
        {children}
        <Text style={{color: "white", fontSize: 16}}>{label}</Text>
      </Box>
    </PressableScale>
  );
};
