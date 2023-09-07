<template>
  <j-tray-plugin
    description='Export Data to a file.'
    :link="'https://lcviz.readthedocs.io/en/'+vdocs+'/plugins.html#export_data'"
    :popout_button="popout_button">

    <plugin-dataset-select
      :items="dataset_items"
      :selected.sync="dataset_selected"
      :show_if_single_entry="true"
      label="Data"
      hint="Select the light curve to export."
    />

    <v-row>
      <v-select
        :menu-props="{ left: true }"
        attach
        :items="format_items.map(i => i.label)"
        v-model="format_selected"
        label="Format"
        hint="File Format."
        persistent-hint
      ></v-select>
    </v-row>

    <v-row justify="end">
      <v-btn
       text
       color="primary"
       @click="save"
       :disabled="dataset_selected.length == 0"
      >
       Save to File
      </v-btn>
    </v-row>

  </j-tray-plugin>
</template>
