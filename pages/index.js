import Project from "@/components/project";
import { Grid, Heading, Image, Text, VStack } from "@chakra-ui/react";

export default function Home() {
  return (
    <Grid placeItems='center' p={3}>
      <Image
        borderRadius="full"
        boxSize="150px"
        src="/FotoMaximo.jpg"
        alt="Máximo Fernández Núñez"
      />
      <VStack>
        <Heading>Máximo Fernández Núñez</Heading>
        <Text>Este es mi portafolio</Text>
      </VStack>
      <Project text="Projecto1"/>
      <Project text="Projecto2"/>
      <Project text="Projecto3"/>
    </Grid>
  );
}
