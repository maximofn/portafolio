import { extendTheme } from "@chakra-ui/react";

const theme = extendTheme({
    styles: {
      global: (props) => ({
        body: {
          margin: 0,
          padding: 0,
          minHeight: "100vh",
          color: 'white', 
          background: 
            //"linear-gradient(90deg, rgba(191,73,97,1) 0%, rgba(220,90,50,1) 100%, rgba(220,90,50,1) 100%)",
            "linear-gradient(90deg, rgba(131,58,180,1) 0%, rgba(236,81,81,1) 0%, rgba(252,133,69,1) 100%)",
        },
        a: {
          color: "violet",
        },
      }),
    },
  });

export default theme;