import { Box } from "@chakra-ui/react";

export default function Project({text}) {
    return (
        <Box w="full" h="100px" _hover={{background: 'rgba(255, 255, 255, 0.2)'}}>
            {text}
        </Box>
    );
}